import sys
import os
import json
import time
import copy
import random
import argparse
import hashlib
import pickle
from collections import defaultdict

# Avoid excessive BLAS/CPU thread allocation on small Windows machines.
# Explicit environment settings still take precedence.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import pandas as pd
import torch
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data.data_params_dict import data_params
from dataset.train_dataset import TrainDataset
from dataset.adaptest_dataset import AdapTestDataset
from model.NCD import NCDModel
from dense_paper import (
    CustomCrossover, CustomMutation, Paper,
    validate_test_length, decode_unique_questions, partition_toeic_stages,
    difficulty_bounds
)
from pcat_routing import rank_medium_paper_mastery


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def save_optimizer_checkpoint(path, spec, algorithm, elapsed_sec):
    state = {
        'version': 1,
        'spec': spec,
        'algorithm': algorithm,
        'elapsed_sec': elapsed_sec,
        'python_random_state': random.getstate(),
        'numpy_random_state': np.random.get_state(),
        'torch_random_state': torch.get_rng_state(),
    }
    temporary = path + '.tmp'
    with open(temporary, 'wb') as target:
        pickle.dump(state, target, protocol=pickle.HIGHEST_PROTOCOL)
        target.flush()
        os.fsync(target.fileno())
    os.replace(temporary, path)


def load_optimizer_checkpoint(path, spec):
    with open(path, 'rb') as source:
        state = pickle.load(source)
    if state.get('version') != 1 or state.get('spec') != spec:
        raise ValueError(f'Optimizer checkpoint does not match this run: {path}')
    random.setstate(state['python_random_state'])
    np.random.set_state(state['numpy_random_state'])
    torch.set_rng_state(state['torch_random_state'])
    return state['algorithm'], float(state['elapsed_sec'])


def evaluate_paper_on_split(
    paper_30, split_stu, split_triplets, concept_map, metadata,
    question_overlap, question_difficulty, part_map, bundle_map,
    ckpt_path, config, seed, allowed_questions,
    adaptive=True, tau=0.0, content_balance=False
):
    """
    Evaluate a two-stage paper using each learner's unadministered questions
    as the query set, following the paper's public implementation.
    """
    paper1, paper2, paper3 = partition_toeic_stages(
        paper_30, question_difficulty, part_map, bundle_map,
        allowed_questions=allowed_questions, content_balance=content_balance
    )
    paper_length = len(paper2)
    test_length = 2 * paper_length
    target_rate = test_length / metadata['prob_num']

    eval_data = AdapTestDataset(
        split_triplets, concept_map,
        metadata['stu_num'], metadata['prob_num'],
        metadata['know_num'], seed
    )
    eval_data.reset2()

    local_cfg = copy.deepcopy(config)
    local_cfg['num_epochs'] = 10
    local_cfg['batch_size'] = 64
    local_cfg['shrinkage_tau'] = tau
    model = NCDModel(**local_cfg)
    model.init_model(eval_data)
    model.adaptest_load(ckpt_path)

    stu_cov = {}
    stu_exp = {}
    partial_concepts = {}
    partial_overlap = {}
    for stu in split_stu:
        concepts = set()
        overlap = 0.0
        for prob in paper2:
            eval_data.apply_selection(stu, prob)
            overlap += (question_overlap[prob] - target_rate) ** 2
            concepts.update(concept_map[prob])
        partial_concepts[stu] = concepts
        partial_overlap[stu] = overlap

    hard_students = set()
    if adaptive:
        hard_students, _ = rank_medium_paper_mastery(
            model, eval_data, split_stu, paper2, concept_map
        )

    for stu in split_stu:
        concepts = partial_concepts[stu]
        overlap = partial_overlap[stu]
        stage2 = paper3 if stu in hard_students else paper1
        for prob in stage2:
            eval_data.apply_selection(stu, prob)
            overlap += (question_overlap[prob] - target_rate) ** 2
            concepts.update(concept_map[prob])

        stu_cov[stu] = len(concepts) / metadata['know_num']
        stu_exp[stu] = overlap / max(target_rate, 1e-8)
        eval_data.meta[stu] = [
            que for que in range(metadata['prob_num'])
            if que not in eval_data._tested[stu]
        ]
        assert len(eval_data._tested[stu]) == test_length
        assert len(eval_data.meta[stu]) == metadata['prob_num'] - test_length

    cov = sum(stu_cov.values()) / max(len(stu_cov), 1)
    exp = sum(stu_exp.values()) / max(len(stu_exp), 1)

    model.update(eval_data, out=False)

    query_metrics = model.evaluate(eval_data)

    return {
        'auc': float(query_metrics['auc']),
        'acc': float(query_metrics['acc']),
        'cov': float(cov),
        'exp': float(exp),
        'hard_branch_students': len(hard_students),
        'easy_branch_students': len(split_stu) - len(hard_students),
        'routing_rule': 'top-half NCD mastery on medium-paper concepts' if adaptive else 'fixed medium-plus-easy',
        'paper1_easy': [int(x) for x in paper1],
        'paper2_medium': [int(x) for x in paper2],
        'paper3_hard': [int(x) for x in paper3],
    }


def get_paper(x, paper_config):
    return decode_unique_questions(
        x,
        paper_config['num_selected'],
        paper_config['question_type'],
        paper_config['question_difficulty'],
        paper_config.get('part_map', None),
        paper_config.get('bundle_map', None),
        content_balance=paper_config.get('content_balance', False),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset', default='Dense_EdNetTOEIC_Balanced90_90d', type=str,
        help='PCAT benchmark dataset (default: first-attempt EdNet 90-day cohort)'
    )
    parser.add_argument('--cdm', default='ncd', type=str, choices=['ncd'], help='NCD only; kept for command compatibility')
    parser.add_argument('--device', default='cpu', type=str)
    parser.add_argument('--test_length', type=int, default=20)
    parser.add_argument('--generations', type=int, default=100, help='NSGA-II generations (paper: 100)')
    parser.add_argument('--population', type=int, default=80, help='NSGA-II population (paper: 80)')
    parser.add_argument('--offspring', type=int, default=50, help='NSGA-II offspring (author code: 50)')
    parser.add_argument('--seeds', default='20,21,22,23,24', help='five independent runs by default')
    parser.add_argument('--content-balance', choices=['auto', 'none', 'listening_reading'], default='auto',
                        help='For TOEIC, give each 10-item stage equal Listening and Reading (default: auto).')
    parser = parser.parse_args()

    seed_list = [int(s.strip()) for s in parser.seeds.split(',') if s.strip()]
    if not seed_list or len(set(seed_list)) != len(seed_list):
        raise ValueError('--seeds must contain distinct integer seeds')
    if parser.generations < 1 or parser.population < 2 or parser.offspring < 1:
        raise ValueError('NSGA-II generations, population and offspring must be positive')

    dataset = parser.dataset
    metadata = {
        'stu_num': data_params[dataset]['stu_num'],
        'prob_num': data_params[dataset]['prob_num'],
        'know_num': data_params[dataset]['know_num'],
    }

    response_logs = pd.read_csv(f'../../data/{dataset}/TotalData.csv', header=None).drop_duplicates()
    q = pd.read_csv(f'../../data/{dataset}/q.csv', header=None)
    with open(f'../../data/{dataset}/question_map.json', 'r') as f:
        question_map = json.load(f)

    cat_path = f'../../data/{dataset}/toeic_question_catalog.csv'
    part_map, bundle_map = None, None
    if os.path.exists(cat_path):
        cat_df = pd.read_csv(cat_path)
        part_map = {int(r['q_idx']): int(r['part']) for _, r in cat_df.iterrows()}
        bundle_map = {int(r['q_idx']): str(r['bundle_id']) for _, r in cat_df.iterrows()}
    content_balance = parser.content_balance == 'listening_reading' or (
        parser.content_balance == 'auto' and part_map is not None
    )
    if content_balance and (part_map is None or bundle_map is None):
        raise ValueError('Listening/Reading balance needs toeic_question_catalog.csv.')
    if content_balance and parser.test_length % 4:
        raise ValueError('Equal Listening/Reading in both stages requires --test_length divisible by 4.')

    exposure_path = f'../../data/{dataset}/question_exposure.csv'
    if os.path.exists(exposure_path):
        exposure_df = pd.read_csv(exposure_path)
        question_overlap = defaultdict(float, {
            int(row['q_idx']): float(row['exposure_rate'])
            for _, row in exposure_df.iterrows()
        })
        if set(question_overlap) != set(range(metadata['prob_num'])):
            raise ValueError(f"Incomplete question exposure table: {exposure_path}")
    else:
        if dataset.replace("Dense_", "") in ["MOOCRadar", "Assistement17", "EdNetTOEIC"]:
            original_response_logs = pd.read_csv(f'../../data/{dataset.replace("Dense_", "")}/TotalData.csv', header=None)
        else:
            original_response_logs = pd.read_csv(f'../../data/{dataset.replace("Dense_", "")}/TotalData.csv')

        question_overlap = defaultdict(int)
        for log in original_response_logs.values:
            if str(int(log[1])) in question_map:
                question_overlap[question_map[str(int(log[1]))]] += 1
        for prob in question_overlap:
            question_overlap[prob] = question_overlap[prob] / data_params[dataset.replace("Dense_", "")]['stu_num']

    concept_map = {
        idx: np.where(np.array(row))[0].tolist()
        for idx, row in enumerate(q.values)
    }

    # The paper selects from the full dense question bank. Query questions are
    # identified separately for each learner after their 20-item test.
    selectable_questions = list(range(metadata['prob_num']))
    num_selected = validate_test_length(parser.test_length, len(selectable_questions))

    print(
        f"Selectable question bank: {len(selectable_questions)} questions "
        f"({parser.test_length} administered, {metadata['prob_num'] - parser.test_length} "
        f"unadministered query questions per learner; num_selected={num_selected})"
    )

    question_type = defaultdict(list)
    know_hash = {}
    cnt = 0
    for que in selectable_questions:
        knows = concept_map[que]
        sorted_knows = tuple(sorted(knows))
        # One type is one Q-matrix attribute combination (paper Sec. 4.1).
        # TOEIC bundles may still introduce repeated types after decoding.
        if sorted_knows not in know_hash:
            know_hash[sorted_knows] = cnt
            cnt += 1
        question_type[know_hash[sorted_knows]].append(que)

    print(f"=== Running Multi-Seed PCAT + NCD on {dataset} (Seeds: {seed_list}) ===")

    per_seed_results = {}
    run_tag = (
        f'{dataset}_paper_query_{parser.generations}gen_'
        f'{parser.population}pop_seeds{"-".join(map(str, seed_list))}'
    )
    if content_balance:
        run_tag += '_balancedLR'
    with open(f'{run_tag}_output.txt', 'w', encoding='utf-8') as file:
        file.write(f"The dataset for the current output file is:{dataset}\n")
        file.write(f"Query set: each learner's unadministered questions from the full question bank\n")

    for seed in seed_list:
        print(f"\n--- Seed {seed} ---")
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        config = {
            'learning_rate': 0.05,
            'batch_size': 512,
            'num_epochs': 10,
            'num_dim': 1,
            'device': parser.device,
            'cdm': 'ncd',
            'prednet_len1': 128,
            'prednet_len2': 64,
            'betas': (0.9, 0.999),
            'policy': 'mynew',
            'policy_path': f'../../model/ckpt/{dataset}_bocat_policy.pt',
            'THRESHOLD': 300,
            'start': 0,
            'end': 3000,
            'seed': seed,
            'shrinkage_tau': 0.0,
        }

        # Separate checkpoints allow independent seed runs without races.
        ckpt_ncd = f'../../model/ckpt/model_{dataset}_seed{seed}_train_ncd.pt'
        active_ckpt = ckpt_ncd
        optimizer_ckpt = (
            f'../../model/ckpt/nsga2_{dataset}_{parser.test_length}items_'
            f'{parser.generations}gen_{parser.population}pop_'
            f'{parser.offspring}offspring_seed{seed}'
            f'{"_balancedLR" if content_balance else ""}.pkl'
        )

        total_stu = list(range(metadata['stu_num']))
        shuffled_stu = total_stu.copy()
        random.shuffle(shuffled_stu)
        n_train = int(len(shuffled_stu) * 0.80)
        train_stu = sorted(shuffled_stu[:n_train])
        test_stu = sorted(shuffled_stu[n_train:])

        train_set = set(train_stu)
        train_triplets, test_triplets = [], []
        for log in response_logs.values:
            s, p, y = int(log[0]), int(log[1]), int(log[2])
            if s in train_set:
                train_triplets.append((s, p, y))
            else:
                test_triplets.append((s, p, y))

        train_data = TrainDataset(
            train_triplets, concept_map,
            metadata['stu_num'], metadata['prob_num'], metadata['know_num']
        )

        model_train = NCDModel(**config)
        model_train.init_model(train_data)
        if os.path.exists(active_ckpt):
            model_train.adaptest_load(active_ckpt)
            print(f'Reusing trained NCD checkpoint for seed {seed}: {active_ckpt}', flush=True)
        else:
            if os.path.exists(optimizer_ckpt):
                raise FileNotFoundError(
                    f'Optimizer checkpoint exists but trained NCD model is missing: {active_ckpt}'
                )
            model_train.train(train_data, out=(seed == seed_list[0]))
            model_train.adaptest_save(active_ckpt)
            print(f'Trained NCD checkpoint for seed {seed}: {active_ckpt}', flush=True)

        train_start_time = time.time()
        raw_k = torch.sigmoid(model_train.model.k_difficulty.weight.data).cpu().numpy().copy()
        question_difficulty = raw_k * q.to_numpy()
        min_difficulty, max_difficulty = difficulty_bounds(question_difficulty)

        paper_config = {
            'metadata': metadata,
            'num_selected': num_selected,
            'concept_map': concept_map,
            'question_overlap': question_overlap,
            'model_true': None,
            'train_stu': train_stu,
            'ckpt_path': active_ckpt,
            'question_difficulty': question_difficulty,
            'device': parser.device,
            'question_type': question_type,
            'cdm': 'ncd',
            'seed': seed,
            'config': config,
            'train_triplets': train_triplets,
            'part_map': part_map,
            'bundle_map': bundle_map,
            'content_balance': content_balance,
            'use_exp': True,
        }

        algorithm = NSGA2(
            pop_size=parser.population,
            n_offsprings=parser.offspring,
            sampling=FloatRandomSampling(),
            crossover=CustomCrossover(num_selected=num_selected, question_type=question_type, a=2, b=2, part_map=part_map),
            mutation=CustomMutation(
                num_selected=num_selected,
                question_type=question_type,
                maxmin_difficulty=[max_difficulty, min_difficulty],
                prob_mutation=0.5,
                part_map=part_map
            ),
            eliminate_duplicates=True
        )

        checkpoint_spec = {
            'dataset': dataset,
            'seed': seed,
            'test_length': parser.test_length,
            'generations': parser.generations,
            'population': parser.population,
            'offspring': parser.offspring,
            'response_sha256': file_sha256(f'../../data/{dataset}/TotalData.csv'),
            'q_sha256': file_sha256(f'../../data/{dataset}/q.csv'),
            'model_sha256': file_sha256(active_ckpt),
        }
        if content_balance:
            checkpoint_spec['content_balance'] = 'listening_reading_stage_half_v1'
            checkpoint_spec['catalog_sha256'] = file_sha256(cat_path)
        elapsed_prior = 0.0
        if os.path.exists(optimizer_ckpt):
            algorithm, elapsed_prior = load_optimizer_checkpoint(
                optimizer_ckpt, checkpoint_spec
            )
            print(
                f'Resuming NSGA-II seed {seed} after generation {algorithm.n_gen - 1}',
                flush=True,
            )
        else:
            algorithm.setup(
                Paper(paper_config),
                termination=('n_gen', parser.generations),
                seed=seed,
                verbose=(seed == seed_list[0]),
            )
        while algorithm.has_next():
            algorithm.next()
            save_optimizer_checkpoint(
                optimizer_ckpt, checkpoint_spec, algorithm,
                elapsed_prior + time.time() - train_start_time,
            )
        res = algorithm.result()
        online_time = elapsed_prior + time.time() - train_start_time

        difficulty_paper = copy.deepcopy(res.pop)
        F = difficulty_paper.get("F")
        X = difficulty_paper.get("X")
        nds = NonDominatedSorting().do(F, only_non_dominated_front=True)

        pareto_candidates = []
        seen_papers = set()
        for i in range(len(nds)):
            cand = get_paper(X[nds[i]].tolist(), paper_config)
            key = tuple(cand)
            if key not in seen_papers:
                seen_papers.add(key)
                pareto_candidates.append((cand, F[nds[i]].tolist()))

        if not pareto_candidates:
            raise RuntimeError('NSGA-II did not return a feasible Pareto paper')
        # Section 5.4 of the paper selects the final Pareto solution by
        # training-set AUC + ACC, with no validation-label access.
        best_idx = max(
            range(len(pareto_candidates)),
            key=lambda k: -pareto_candidates[k][1][2] - pareto_candidates[k][1][3]
        )
        best_paper = pareto_candidates[best_idx][0]

        # Held-out Test Set Evaluation
        test_start_time = time.time()
        test_proposed = evaluate_paper_on_split(
            best_paper, test_stu, test_triplets, concept_map, metadata,
            question_overlap, question_difficulty, part_map, bundle_map,
            active_ckpt, config, seed, selectable_questions,
            adaptive=True, tau=0.0, content_balance=content_balance
        )
        offline_time = time.time() - test_start_time

        test_shrinkage = evaluate_paper_on_split(
            best_paper, test_stu, test_triplets, concept_map, metadata,
            question_overlap, question_difficulty, part_map, bundle_map,
            active_ckpt, config, seed, selectable_questions,
            adaptive=True, tau=1.0, content_balance=content_balance
        )
        test_fixed_paper = evaluate_paper_on_split(
            best_paper, test_stu, test_triplets, concept_map, metadata,
            question_overlap, question_difficulty, part_map, bundle_map,
            active_ckpt, config, seed, selectable_questions,
            adaptive=False, tau=0.0, content_balance=content_balance
        )

        # Random baseline samples from the same full question bank.
        rand_metrics = []
        for r_seed in [101, 102, 103]:
            rng = random.Random(seed * 1000 + r_seed)
            rand_raw = rng.sample(selectable_questions, num_selected)
            p1_r, p2_r, p3_r = partition_toeic_stages(
                rand_raw, question_difficulty, part_map, bundle_map,
                allowed_questions=selectable_questions, content_balance=content_balance
            )
            rand_paper = p1_r + p2_r + p3_r
            rm = evaluate_paper_on_split(
                rand_paper, test_stu, test_triplets, concept_map, metadata,
                question_overlap, question_difficulty, part_map, bundle_map,
                active_ckpt, config, seed, selectable_questions,
                adaptive=False, tau=0.0, content_balance=content_balance
            )
            rand_metrics.append(rm)
        test_random = {
            k: float(np.mean([m[k] for m in rand_metrics]))
            for k in ['auc', 'acc', 'cov', 'exp']
        }

        per_seed_results[str(seed)] = {
            'paper_assembly_time_sec': round(online_time, 2),
            'test_inference_time_sec': round(offline_time, 4),
            'selected_paper': {
                'full_30': best_paper,
                'stage1_medium_10': test_proposed['paper2_medium'],
                'stage2a_easy_10': test_proposed['paper1_easy'],
                'stage2b_hard_10': test_proposed['paper3_hard'],
                'stage_content_counts': {
                    label: {
                        'listening': sum(part_map[q] in (1, 2, 3, 4) for q in test_proposed[key]),
                        'reading': sum(part_map[q] in (5, 6, 7) for q in test_proposed[key]),
                    }
                    for label, key in [('medium', 'paper2_medium'), ('easy', 'paper1_easy'),
                                       ('hard', 'paper3_hard')]
                } if part_map is not None else None,
                'administered_path_content_counts': {
                    label: {
                        'listening': sum(part_map[q] in (1, 2, 3, 4)
                                         for q in test_proposed['paper2_medium'] + test_proposed[key]),
                        'reading': sum(part_map[q] in (5, 6, 7)
                                       for q in test_proposed['paper2_medium'] + test_proposed[key]),
                    }
                    for label, key in [('medium_then_easy', 'paper1_easy'),
                                       ('medium_then_hard', 'paper3_hard')]
                } if part_map is not None else None,
            },
            'methods': {
                '1_Random_20_Items_NCD': test_random,
                '2_Fixed_NonAdaptive_20_Items_NCD': test_fixed_paper,
                '3_PCAT_PaperMasteryRank_NCD': test_proposed,
                '4_PCAT_PaperMasteryRank_NCD_ShrinkageAblation': test_shrinkage,
            }
        }

        with open(f'{run_tag}_output.txt', 'a', encoding='utf-8') as file:
            file.write(f"seed:{seed} | Split: Train={len(train_stu)}, Test={len(test_stu)}\n")
            file.write(f"The selected final paper (max training AUC+ACC):{best_paper}\n")
            file.write(
                f"The evaluation results on the test set: "
                f"Query{metadata['prob_num'] - parser.test_length}_AUC:{test_proposed['auc']:.4f} "
                f"Query{metadata['prob_num'] - parser.test_length}_ACC:{test_proposed['acc']:.4f} "
                f"COV:{test_proposed['cov']:.4f}, EXP:{test_proposed['exp']:.4f}, "
                f"assembly:{online_time:.2f}s, inference:{offline_time:.4f}s\n"
            )

    # Aggregate Mean ± Std across seeds
    method_names = list(per_seed_results[str(seed_list[0])]['methods'].keys())
    aggregated = {}
    for m_name in method_names:
        aggregated[m_name] = {}
        for metric in ['auc', 'acc', 'cov', 'exp']:
            vals = [per_seed_results[str(s)]['methods'][m_name][metric] for s in seed_list]
            aggregated[m_name][f'{metric}_mean'] = round(float(np.mean(vals)), 4)
            aggregated[m_name][f'{metric}_std'] = round(float(np.std(vals)), 4)

    first_seed = per_seed_results[str(seed_list[0])]
    benchmark_summary = {
        'seeds_evaluated': seed_list,
        'split_ratio': f'80% Train ({len(train_stu)}) / 20% Test ({len(test_stu)})',
        'methodology': {
            'source': 'https://doi.org/10.1145/3711896.3737073',
            'routing': 'NCD mastery percentile on medium-paper concepts; top half hard, bottom half easy',
            'objectives': ['AUC', 'ACC', 'COV', 'EXP'],
            'paper_selection': 'highest training AUC plus ACC from final Pareto population',
            'population': parser.population,
            'offspring': parser.offspring,
            'generations': parser.generations,
            'query_protocol': 'all unadministered items per learner after the simulated test',
            'dataset_adaptation': 'EdNet TOEIC, whole bundles, Q-matrix tags',
            'content_balance': '5 Listening + 5 Reading in each 10-item stage' if content_balance else 'none',
        },
        'query_questions_per_learner': metadata['prob_num'] - parser.test_length,
        'selectable_candidate_pool_size': len(selectable_questions),
        f'timing_seed{seed_list[0]}': {
            'nsga2_optimization_sec': first_seed['paper_assembly_time_sec'],
            'test_inference_sec': first_seed['test_inference_time_sec'],
        },
        f'selected_paper_seed{seed_list[0]}': first_seed['selected_paper'],
        'multi_seed_summary_mean_std': aggregated,
        'per_seed_details': per_seed_results,
    }
    benchmark_output_path = f'{run_tag}_benchmark_evaluation_results.json'
    with open(benchmark_output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark_summary, f, indent=2)
    print(f"Saved benchmark results to {benchmark_output_path}")

    print(f"\n=== MULTI-SEED ({len(seed_list)} SPLITS) TOEIC-ADAPTED PCAT BENCHMARK (MEAN ± STD) ===")
    for m_name, stats in aggregated.items():
        print(
            f"{m_name:38s} | Query{metadata['prob_num'] - parser.test_length} "
            f"AUC: {stats['auc_mean']:.4f}±{stats['auc_std']:.4f}, "
            f"ACC: {stats['acc_mean']:.4f}±{stats['acc_std']:.4f} | "
            f"COV: {stats['cov_mean']:.4f}"
        )
