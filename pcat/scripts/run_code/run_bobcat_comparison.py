"""Train BOBCAT-ST on EdNet train learners and compare with saved PCAT papers.

The auxiliary NCD meta-learner and bilevel updates come from bobcat_train.py.
Final scoring uses exactly the existing PCAT NCD checkpoint/update protocol.
BOBCAT and uniform Random select individual items without TOEIC bundle repair.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

import numpy as np
import pandas as pd
import torch

from bobcat_train import MAMLModel, run_biased
from data.data_params_dict import data_params
from dataset.adaptest_dataset import AdapTestDataset
from model.NCD import NCDModel
from model.utils import Actor, StraightThrough
from pcat_routing import rank_medium_paper_mastery

METRICS = ('auc', 'acc', 'cov', 'exp', 'broken_bundle_test_rate',
           'incomplete_bundle_rate', 'selection_sec', 'diagnosis_sec', 'online_total_sec')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def retry_file_operation(operation, *args, attempts=21, delay=.25, **kwargs):
    """Windows indexers/sync clients can briefly deny rename or write access."""
    for attempt in range(attempts):
        try:
            return operation(*args, **kwargs)
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)


def write_json(path, value):
    temporary = Path(str(path) + '.tmp')
    retry_file_operation(temporary.write_text,
                         json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    retry_file_operation(temporary.replace, path)


def write_status(path, status):
    # Progress reporting is optional. A locked status file must not stop training
    # or hide the original exception. Checkpoint/result failures remain fatal.
    try:
        write_json(path, status)
    except OSError as exc:
        print(f'WARNING: could not update progress file {path}: {exc}',
              file=sys.stderr, flush=True)


def split_students(n_students, seed):
    ids = list(range(n_students))
    random.Random(seed).shuffle(ids)
    split = int(n_students * .8)
    return sorted(ids[:split]), sorted(ids[split:])


class PolicyTrainDataset(torch.utils.data.Dataset):
    """Only outer-training learners; disjoint support/query items per learner."""
    def __init__(self, train_responses, seed, test_length):
        labels = torch.as_tensor(train_responses, dtype=torch.float32)
        support_count = int(labels.shape[1] * .8)
        if not 0 < test_length <= support_count < labels.shape[1]:
            raise ValueError('Need enough support items and a nonempty policy query set')
        rng = np.random.default_rng(seed)
        support = torch.zeros_like(labels, dtype=torch.long)
        for row in range(len(labels)):
            support[row, rng.permutation(labels.shape[1])[:support_count]] = 1
        query = 1 - support
        self.batch = {
            'input_labels': labels * support,
            'input_mask': support,
            'output_labels': labels * query,
            'output_mask': query,
        }

    def __len__(self):
        return len(self.batch['input_labels'])

    def __getitem__(self, index):
        return {key: value[index] for key, value in self.batch.items()}


def policy_rollout(policy, responses, length):
    """Reveal an answer only AFTER choosing its item. No update of policy at test."""
    policy.eval()
    responses = torch.as_tensor(responses, dtype=torch.float32)
    state = torch.zeros_like(responses)
    available = torch.ones_like(responses)
    rows = torch.arange(len(responses))
    history = []
    with torch.no_grad():
        for _ in range(length):
            _, actions = policy(state, available)
            actions = actions.reshape(-1)
            if not torch.all(available[rows, actions] == 1):
                raise RuntimeError('Repeated or unavailable question selected')
            history.append(actions.clone())
            # Only these selected answers are read from the response matrix.
            state[rows, actions] = responses[rows, actions] * 2 - 1
            available[rows, actions] = 0
    return torch.stack(history, dim=1).tolist()


def bundle_metrics(selections, bundles):
    grouped = {}
    for qid, bid in bundles.items():
        grouped.setdefault(bid, set()).add(qid)
    groups = [group for group in grouped.values() if len(group) > 1]
    broken_tests = incomplete = touched = 0
    for questions in selections.values():
        selected = set(questions)
        broken = False
        for group in groups:
            count = len(group & selected)
            if count:
                touched += 1
                if count < len(group):
                    incomplete += 1
                    broken = True
        broken_tests += int(broken)
    return {
        'broken_bundle_test_rate': broken_tests / len(selections),
        'incomplete_bundle_rate': incomplete / touched if touched else 0.0,
        'touched_multitem_bundles': touched,
        'incomplete_multitem_bundles': incomplete,
    }


def ncd_config(seed):
    return dict(learning_rate=.05, batch_size=64, num_epochs=10, device='cpu',
                prednet_len1=128, prednet_len2=64, policy='mynew',
                betas=(.9, .999), seed=seed, shrinkage_tau=0.0)


def make_evaluator(problem, test_ids, seed, checkpoint):
    test_set = set(test_ids)
    triplets = [tuple(map(int, row)) for row in problem['logs'] if int(row[0]) in test_set]
    meta = problem['metadata']
    data = AdapTestDataset(triplets, problem['concepts'], meta['stu_num'],
                          meta['prob_num'], meta['know_num'], seed)
    data.reset2()
    model = NCDModel(**ncd_config(seed))
    model.init_model(data)
    model.adaptest_load(str(checkpoint))
    return data, model


def score_selection(problem, data, model, selections, length, selection_sec):
    """Common final NCD fit and unadministered-query scoring for every method."""
    bank_size = problem['metadata']['prob_num']
    for sid, questions in selections.items():
        if len(questions) != length or len(set(questions)) != length:
            raise ValueError('Each learner must receive exactly T distinct questions')
        if list(data.tested[sid]) != questions:
            raise ValueError('Selection history differs from observed-response history')
        data.meta[sid] = [q for q in range(bank_size) if q not in set(questions)]
        assert len(data.meta[sid]) == bank_size - length
    started = time.perf_counter()
    model.update(data, out=False)
    scored = model.evaluate(data)
    elapsed = time.perf_counter() - started
    cov = np.mean([len({c for q in qs for c in problem['concepts'][q]}) /
                   problem['metadata']['know_num'] for qs in selections.values()])
    target = length / bank_size
    exp = np.mean([sum((problem['exposure'][q] - target) ** 2 for q in qs) / target
                   for qs in selections.values()])
    return dict(auc=float(scored['auc']), acc=float(scored['acc']), cov=float(cov),
                exp=float(exp), **bundle_metrics(selections, problem['bundles']),
                selection_sec=selection_sec, diagnosis_sec=elapsed,
                online_total_sec=selection_sec + elapsed,
                selected_questions={str(s): list(map(int, qs)) for s, qs in selections.items()})


def evaluate_method(problem, test_ids, seed, checkpoint, length, method,
                    policy=None, paper=None, random_repeat=0):
    data, model = make_evaluator(problem, test_ids, seed, checkpoint)
    started = time.perf_counter()
    if method in ('PCAT', 'Fixed_medium_easy'):
        medium = paper['stage1_medium_10']
        easy, hard = paper['stage2a_easy_10'], paper['stage2b_hard_10']
        assert len(medium) == len(easy) == len(hard) == length // 2
        for sid in test_ids:
            for q in medium:
                data.apply_selection(sid, q)
        hard_students = set()
        if method == 'PCAT':
            hard_students, _ = rank_medium_paper_mastery(
                model, data, test_ids, medium, problem['concepts'])
        selections = {}
        for sid in test_ids:
            branch = hard if sid in hard_students else easy
            for q in branch:
                data.apply_selection(sid, q)
            selections[sid] = list(medium) + list(branch)
    else:
        if method == 'BOBCAT_ST':
            selected = policy_rollout(policy, problem['responses'][test_ids], length)
        elif method == 'Random_item':
            rng = np.random.default_rng(seed * 1000 + 101 + random_repeat)
            selected = [rng.choice(problem['metadata']['prob_num'], length, replace=False).tolist()
                        for _ in test_ids]
        else:
            raise ValueError(method)
        selections = dict(zip(test_ids, selected))
        for sid, qs in selections.items():
            for q in qs:
                data.apply_selection(sid, q)
    selection_sec = time.perf_counter() - started
    result = score_selection(problem, data, model, selections, length, selection_sec)
    if method == 'PCAT':
        result['hard_branch_students'] = len(hard_students)
    return result


def train_policy(problem, train_ids, seed, args, spec, checkpoint, progress):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    q = torch.tensor(problem['q'], dtype=torch.float32)
    n_questions, n_concepts = q.shape
    proxy = MAMLModel(n_questions, question_dim=n_concepts, n_query=args.test_length,
                      emb=q, tp='ncd', device='cpu')
    prior = [torch.zeros((1, n_concepts), requires_grad=True)]
    optimizer = torch.optim.Adam(proxy.parameters(), lr=1e-4, weight_decay=1e-8)
    prior_optimizer = torch.optim.SGD(prior, lr=1e-4, weight_decay=2e-6, momentum=.9)
    policy = StraightThrough(n_questions, n_questions, 2e-3,
                             {'device': 'cpu', 'betas': (.9, .999)})
    cfg = dict(mode='train', inner_loop=5, inner_lr=.1, n_query=args.test_length)
    # Construct this dataset only from the outer train subset, never test responses.
    dataset = PolicyTrainDataset(problem['responses'][train_ids], seed, args.test_length)
    last_epoch, elapsed, history = 0, 0.0, []
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location='cpu', weights_only=False)
        if saved['spec'] != spec:
            raise ValueError(f'Checkpoint provenance mismatch: {checkpoint}')
        proxy.load_state_dict(saved['proxy'])
        prior[0].data.copy_(saved['prior'])
        policy.policy.load_state_dict(saved['policy'])
        optimizer.load_state_dict(saved['optimizer'])
        prior_optimizer.load_state_dict(saved['prior_optimizer'])
        policy.optimizer.load_state_dict(saved['policy_optimizer'])
        torch.set_rng_state(saved['torch_rng'])
        random.setstate(saved['python_rng'])
        np.random.set_state(saved['numpy_rng'])
        last_epoch, elapsed, history = saved['epoch'], saved['elapsed_sec'], saved['history']
    started = time.perf_counter()
    for epoch in range(last_epoch + 1, args.epochs + 1):
        generator = torch.Generator().manual_seed(seed * 10000 + epoch)
        loader = torch.utils.data.DataLoader(dataset, batch_size=args.batch_size,
                                            shuffle=True, drop_last=False, generator=generator)
        losses = []
        policy.policy.train()
        for batch in loader:
            output = run_biased(proxy, batch, cfg, optimizer, prior_optimizer, prior, policy)
            if not np.isfinite(output).all():
                raise FloatingPointError('Nonfinite BOBCAT predictions')
            p = np.clip(output, 1e-7, 1 - 1e-7)
            y, mask = batch['output_labels'].numpy(), batch['output_mask'].numpy()
            losses.append(float((-(y * np.log(p) + (1 - y) * np.log(1 - p)) * mask).sum() /
                                mask.sum()))
            if not torch.all(cfg['train_mask'].sum(1) == args.test_length):
                raise RuntimeError('Training rollout did not select T distinct support questions')
            if torch.any(cfg['train_mask'].detach() * batch['output_mask']):
                raise RuntimeError('Policy selected an inner-query question')
        if not all(torch.isfinite(p).all() for p in policy.policy.parameters()):
            raise FloatingPointError('Nonfinite policy weights')
        total_elapsed = elapsed + time.perf_counter() - started
        history.append(dict(epoch=epoch, train_query_bce=float(np.mean(losses)),
                            elapsed_sec=total_elapsed))
        if epoch % 5 == 0 or epoch == args.epochs:
            saved = dict(spec=spec, epoch=epoch, elapsed_sec=total_elapsed, history=history,
                         proxy=proxy.state_dict(), prior=prior[0].detach(),
                         policy=policy.policy.state_dict(), optimizer=optimizer.state_dict(),
                         prior_optimizer=prior_optimizer.state_dict(),
                         policy_optimizer=policy.optimizer.state_dict(),
                         torch_rng=torch.get_rng_state(), python_rng=random.getstate(),
                         numpy_rng=np.random.get_state())
            temporary = Path(str(checkpoint) + '.tmp')
            retry_file_operation(torch.save, saved, temporary)
            retry_file_operation(temporary.replace, checkpoint)
            print(f'seed={seed} epoch={epoch}/{args.epochs} '
                  f'train_query_bce={history[-1]["train_query_bce"]:.5f} '
                  f'elapsed={total_elapsed:.1f}s', flush=True)
        progress(seed, 'training', epoch, total_elapsed)
    policy.policy.eval()
    return policy.policy, history, (history[-1]['elapsed_sec'] if history else elapsed)


def load_problem(dataset):
    folder = ROOT / 'data' / dataset
    meta = {k: data_params[dataset][k] for k in ('stu_num', 'prob_num', 'know_num')}
    logs = pd.read_csv(folder / 'TotalData.csv', header=None).drop_duplicates().to_numpy()
    q = pd.read_csv(folder / 'q.csv', header=None).to_numpy()
    responses = np.full((meta['stu_num'], meta['prob_num']), -1, dtype=np.int64)
    for s, item, answer in logs:
        s, item, answer = int(s), int(item), int(answer)
        if responses[s, item] != -1 or answer not in (0, 1):
            raise ValueError('Duplicate student/item or nonbinary answer')
        responses[s, item] = answer
    if np.any(responses < 0) or q.shape != (meta['prob_num'], meta['know_num']):
        raise ValueError('Expected a complete dense response matrix and matching Q matrix')
    catalog = pd.read_csv(folder / 'toeic_question_catalog.csv')
    exposure = pd.read_csv(folder / 'question_exposure.csv')
    return dict(logs=logs, q=q, responses=responses, metadata=meta,
                concepts={i: np.flatnonzero(row).tolist() for i, row in enumerate(q)},
                bundles={int(r.q_idx): str(r.bundle_id) for r in catalog.itertuples()},
                exposure={int(r.q_idx): float(r.exposure_rate) for r in exposure.itertuples()},
                hashes={name: sha256(folder / name) for name in
                        ('TotalData.csv', 'q.csv', 'toeic_question_catalog.csv', 'question_exposure.csv')})


def aggregate(details):
    if not details:
        return {}
    return {method: {f'{metric}_{stat}': float(fn([seed['methods'][method][metric]
                                                for seed in details.values()]))
                     for metric in METRICS for stat, fn in (('mean', np.mean), ('std', np.std))}
            for method in next(iter(details.values()))['methods']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', default='Dense_EdNetTOEIC_Balanced90_90d')
    parser.add_argument('--seeds', default='20,21,22,23,24')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--test-length', type=int, default=20)
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--run-label', default='full')
    args = parser.parse_args()
    seeds = [int(x) for x in args.seeds.split(',')]
    if len(seeds) != len(set(seeds)) or min(args.epochs, args.batch_size, args.threads) < 1:
        raise ValueError('Invalid run configuration')
    if args.test_length != 20:
        raise ValueError('The saved PCAT reference is for 20-item tests')
    if not args.run_label.replace('_', '').isalnum():
        raise ValueError('run-label must be alphanumeric/underscore')
    torch.set_num_threads(args.threads)
    output_dir = Path(__file__).resolve().parent
    tag = f'{args.dataset}_bobcat_{args.run_label}_{args.epochs}epochs_seeds{"-".join(map(str, seeds))}'
    result_path = output_dir / f'{tag}_comparison_results.json'
    status_path = output_dir / f'bobcat_{args.run_label}_status.json'
    reference_path = output_dir / (f'{args.dataset}_paper_query_100gen_80pop_'
                                   'seeds20-21-22-23-24_benchmark_evaluation_results.json')
    reference = json.loads(reference_path.read_text(encoding='utf-8'))
    problem = load_problem(args.dataset)
    source_hashes = {str(p.relative_to(ROOT)): sha256(p) for p in
                     (Path(__file__), ROOT / 'scripts/bobcat_train.py', ROOT / 'model/utils.py',
                      ROOT / 'model/NCD.py', ROOT / 'scripts/pcat_routing.py')}
    spec_common = dict(version=1, dataset=args.dataset, epochs=args.epochs,
                       batch_size=args.batch_size, test_length=args.test_length,
                       threads=args.threads, data_hashes=problem['hashes'],
                       source_hashes=source_hashes, reference_sha256=sha256(reference_path))
    status = dict(state='running', process_id=os.getpid(), seeds_requested=seeds,
                  configuration=spec_common, progress={})
    results = dict(configuration=spec_common, seeds_requested=seeds, per_seed_details={},
                   methodology={
                       'policy': 'BOBCAT straight-through bilevel optimization, local NCD meta-learner',
                       'policy_training': '100 fixed epochs by default; outer-train learners only; no test tuning',
                       'policy_support_query': 'per-learner seeded 80/20 item split inside outer train',
                       'hyperparameters': dict(inner_loop=5, inner_lr=.1, model_lr=1e-4,
                                               meta_lr=1e-4, policy_lr=2e-3, actor_width=256),
                       'final_scoring': 'same per-seed NCD checkpoint, 10 epochs, batch 64, tau=0',
                       'query': '70 unadministered questions per learner; IDs may differ by method',
                       'constraints': 'BOBCAT/Random individual items; PCAT/Fixed whole TOEIC bundles',
                       'random': 'uniform 20 distinct items per learner, mean of 3 repetitions per split',
                       'fixed': 'saved PCAT medium+easy paper; not independently optimized',
                       'timing': 'CPU wall time per test cohort; model loading excluded; no real exam UI/I/O',
                       'reference': str(reference_path),
                       'sources': ['https://github.com/arghosh/BOBCAT', 'https://github.com/ECNU-ILOG/PCAT'],
                   })

    def progress(seed, phase, epoch, elapsed):
        status['updated_utc'] = datetime.now(timezone.utc).isoformat()
        status['progress'][str(seed)] = dict(phase=phase, completed_epoch=epoch,
                                            training_elapsed_sec=elapsed)
        write_status(status_path, status)

    try:
        for seed in seeds:
            train_ids, test_ids = split_students(problem['metadata']['stu_num'], seed)
            assert not set(train_ids) & set(test_ids)
            ckpt = ROOT / 'model/ckpt' / f'model_{args.dataset}_seed{seed}_train_ncd.pt'
            if not ckpt.exists() or str(seed) not in reference['per_seed_details']:
                raise ValueError(f'Missing PCAT checkpoint/reference for seed {seed}')
            spec = dict(spec_common, seed=seed, train_ids=train_ids, test_ids=test_ids,
                        ncd_sha256=sha256(ckpt))
            checkpoint = ROOT / 'model/ckpt' / f'bobcat_{args.dataset}_{args.run_label}_seed{seed}.pt'
            progress(seed, 'starting', 0, 0)
            policy, history, elapsed = train_policy(problem, train_ids, seed, args, spec, checkpoint, progress)
            progress(seed, 'evaluating', args.epochs, elapsed)
            paper = reference['per_seed_details'][str(seed)]['selected_paper']
            methods = {}
            for name in ('PCAT', 'Fixed_medium_easy', 'BOBCAT_ST'):
                methods[name] = evaluate_method(problem, test_ids, seed, ckpt, args.test_length,
                                                name, policy=policy, paper=paper)
                print(f'seed={seed} {name}: AUC={methods[name]["auc"]:.6f} '
                      f'ACC={methods[name]["acc"]:.6f}', flush=True)
            for name, old_name in [('PCAT', '3_PCAT_PaperMasteryRank_NCD'),
                                   ('Fixed_medium_easy', '2_Fixed_NonAdaptive_20_Items_NCD')]:
                old = reference['per_seed_details'][str(seed)]['methods'][old_name]
                for metric in ('auc', 'acc', 'cov', 'exp'):
                    if not np.isclose(methods[name][metric], old[metric], atol=1e-7, rtol=0):
                        raise ValueError(f'PCAT reference replay mismatch: seed={seed} {name} {metric}')
            random_runs = [evaluate_method(problem, test_ids, seed, ckpt, args.test_length,
                                           'Random_item', random_repeat=r) for r in range(3)]
            methods['Random_item'] = {m: float(np.mean([r[m] for r in random_runs])) for m in METRICS}
            methods['Random_item']['repetitions'] = random_runs
            results['per_seed_details'][str(seed)] = dict(
                train_students=train_ids, test_students=test_ids, methods=methods,
                policy_training_sec=elapsed, training_history=history,
                policy_checkpoint=str(checkpoint), policy_checkpoint_sha256=sha256(checkpoint),
                ncd_checkpoint_sha256=sha256(ckpt), reference_replay_passed=True)
            results['summary_mean_std'] = aggregate(results['per_seed_details'])
            results['state'] = 'complete' if len(results['per_seed_details']) == len(seeds) else 'partial'
            write_json(result_path, results)
            progress(seed, 'complete', args.epochs, elapsed)
        status['state'] = 'complete'
        status['result_path'] = str(result_path)
        write_status(status_path, status)
        print(json.dumps(results['summary_mean_std'], indent=2), flush=True)
        print(f'Results: {result_path}', flush=True)
    except BaseException as exc:
        status['state'] = 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed'
        status['error'] = repr(exc)
        write_status(status_path, status)
        raise


if __name__ == '__main__':
    main()
