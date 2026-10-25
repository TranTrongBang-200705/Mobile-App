"""Replay the balanced PCAT two-stage routing on an existing held-out split."""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

from data.data_params_dict import data_params
from dataset.adaptest_dataset import AdapTestDataset
from model.NCD import NCDModel
from pcat_routing import rank_medium_paper_mastery


def run_simulation(result_path, seed, output_path):
    with result_path.open(encoding='utf-8') as source:
        benchmark = json.load(source)
    if seed not in benchmark['seeds_evaluated']:
        raise ValueError(f'Seed {seed} is absent from {result_path}')
    selected = benchmark['per_seed_details'][str(seed)]['selected_paper']
    stages = {
        'medium': selected['stage1_medium_10'],
        'easy': selected['stage2a_easy_10'],
        'hard': selected['stage2b_hard_10'],
    }
    dataset = 'Dense_EdNetTOEIC_Balanced90_90d'
    data_dir = ROOT / 'data' / dataset
    catalog = pd.read_csv(data_dir / 'toeic_question_catalog.csv')
    part_map = dict(zip(catalog.q_idx.astype(int), catalog.part.astype(int)))
    bundle_map = dict(zip(catalog.q_idx.astype(int), catalog.bundle_id.astype(str)))
    question_ids = dict(zip(catalog.q_idx.astype(int), catalog.question_id.astype(str)))
    q_matrix = pd.read_csv(data_dir / 'q.csv', header=None).to_numpy()
    concept_map = {q: np.flatnonzero(row).tolist() for q, row in enumerate(q_matrix)}
    logs = pd.read_csv(data_dir / 'TotalData.csv', header=None).drop_duplicates()
    responses = {(int(s), int(q)): int(correct) for s, q, correct in logs.itertuples(index=False, name=None)}

    params = data_params[dataset]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    student_ids = list(range(params['stu_num']))
    random.shuffle(student_ids)
    cutoff = int(0.8 * len(student_ids))
    held_out = sorted(student_ids[cutoff:])
    held_out_set = set(held_out)
    test_triplets = [
        (int(s), int(q), int(correct))
        for s, q, correct in logs.itertuples(index=False, name=None)
        if int(s) in held_out_set
    ]
    data = AdapTestDataset(
        test_triplets, concept_map, params['stu_num'], params['prob_num'],
        params['know_num'], seed,
    )
    data.reset2()
    for student in held_out:
        for q in stages['medium']:
            data.apply_selection(student, q)

    config = {
        'learning_rate': 0.05, 'batch_size': 64, 'num_epochs': 10,
        'num_dim': 1, 'device': 'cpu', 'cdm': 'ncd',
        'prednet_len1': 128, 'prednet_len2': 64,
        'betas': (0.9, 0.999), 'policy': 'mynew',
        'policy_path': str(ROOT / 'model' / 'ckpt' / f'{dataset}_bocat_policy.pt'),
        'THRESHOLD': 300, 'start': 0, 'end': 3000,
        'seed': seed, 'shrinkage_tau': 0.0,
    }
    model = NCDModel(**config)
    model.init_model(data)
    checkpoint = ROOT / 'model' / 'ckpt' / f'model_{dataset}_seed{seed}_train_ncd.pt'
    model.adaptest_load(str(checkpoint))
    raw_difficulty = torch.sigmoid(model.model.k_difficulty.weight).detach().cpu().numpy() * q_matrix
    item_difficulty = {
        q: float(raw_difficulty[q][q_matrix[q] != 0].mean())
        for q in range(len(q_matrix))
    }
    hard_students, mastery = rank_medium_paper_mastery(
        model, data, held_out, stages['medium'], concept_map,
    )

    def counts(questions):
        return {
            'listening': sum(part_map[q] in (1, 2, 3, 4) for q in questions),
            'reading': sum(part_map[q] in (5, 6, 7) for q in questions),
        }

    def validate_path(questions):
        if len(questions) != 20 or len(set(questions)) != 20 or counts(questions) != {'listening': 10, 'reading': 10}:
            raise AssertionError('A routed 20-item paper violates the balance rule.')
        for q in questions:
            members = {other for other, bundle in bundle_map.items() if bundle == bundle_map[q]}
            if not members.issubset(questions):
                raise AssertionError(f'Split TOEIC bundle: {bundle_map[q]}')

    details = {}
    grouped = defaultdict(lambda: {'easy': [], 'hard': []})
    for student in held_out:
        branch = 'hard' if student in hard_students else 'easy'
        paper = stages['medium'] + stages[branch]
        validate_path(paper)
        common_correct = sum(responses[student, q] for q in stages['medium'])
        branch_correct = sum(responses[student, q] for q in stages[branch])
        details[student] = {
            'student_id': student,
            'common_correct': common_correct,
            'common_listening_correct': sum(responses[student, q] for q in stages['medium'] if part_map[q] <= 4),
            'common_reading_correct': sum(responses[student, q] for q in stages['medium'] if part_map[q] >= 5),
            'mastery_score': round(mastery[student], 6),
            'branch': branch,
            'branch_correct': branch_correct,
            'total_correct': common_correct + branch_correct,
            'path_content_counts': counts(paper),
            'common_answers': [
                {'q_idx': q, 'question_id': question_ids[q], 'part': part_map[q], 'correct': responses[student, q]}
                for q in stages['medium']
            ],
            'branch_answers': [
                {'q_idx': q, 'question_id': question_ids[q], 'part': part_map[q], 'correct': responses[student, q]}
                for q in stages[branch]
            ],
        }
        grouped[common_correct][branch].append(student)

    shared_scores = [score for score, students in grouped.items() if students['easy'] and students['hard']]
    if shared_scores:
        score = min(shared_scores, key=lambda n: (abs(n - 7), -n))
        easy_id = max(grouped[score]['easy'], key=lambda s: mastery[s])
        hard_id = min(grouped[score]['hard'], key=lambda s: mastery[s])
        same_common_correct = True
    else:
        easy_id = max((s for s in held_out if s not in hard_students), key=lambda s: mastery[s])
        hard_id = min(hard_students, key=lambda s: mastery[s])
        same_common_correct = False

    expected = benchmark['per_seed_details'][str(seed)]['methods']['3_PCAT_PaperMasteryRank_NCD']
    if len(hard_students) != expected['hard_branch_students']:
        raise AssertionError('Simulation routing differs from the saved benchmark.')
    report = {
        'dataset': dataset,
        'seed': seed,
        'source_benchmark': result_path.name,
        'simulation_only': True,
        'held_out_students': len(held_out),
        'branch_counts': {'easy': len(held_out) - len(hard_students), 'hard': len(hard_students)},
        'stage_content_counts': {name: counts(qs) for name, qs in stages.items()},
        'stage_mean_ncd_item_difficulty': {
            name: round(float(np.mean([item_difficulty[q] for q in qs])), 6)
            for name, qs in stages.items()
        },
        'routing_boundary': {
            'highest_easy_mastery': round(max(mastery[s] for s in held_out if s not in hard_students), 6),
            'lowest_hard_mastery': round(min(mastery[s] for s in hard_students), 6),
        },
        'path_content_counts': {
            'medium_then_easy': counts(stages['medium'] + stages['easy']),
            'medium_then_hard': counts(stages['medium'] + stages['hard']),
        },
        'same_common_correct_in_examples': same_common_correct,
        'examples': {'easy': details[easy_id], 'hard': details[hard_id]},
    }
    with output_path.open('w', encoding='utf-8') as target:
        json.dump(report, target, indent=2, ensure_ascii=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=99)
    parser.add_argument(
        '--result', type=Path,
        default=Path(__file__).resolve().parent /
        'Dense_EdNetTOEIC_Balanced90_90d_paper_query_1gen_4pop_seeds99_balancedLR_benchmark_evaluation_results.json',
    )
    parser.add_argument(
        '--output', type=Path,
        default=Path(__file__).resolve().parent / 'balancedLR_simulation_seed99.json',
    )
    args = parser.parse_args()
    summary = run_simulation(args.result, args.seed, args.output)
    print(json.dumps({
        'held_out_students': summary['held_out_students'],
        'branch_counts': summary['branch_counts'],
        'path_content_counts': summary['path_content_counts'],
        'stage_mean_ncd_item_difficulty': summary['stage_mean_ncd_item_difficulty'],
        'routing_boundary': summary['routing_boundary'],
        'same_common_correct_in_examples': summary['same_common_correct_in_examples'],
        'examples': {
            route: {key: value for key, value in detail.items()
                    if key not in ('common_answers', 'branch_answers')}
            for route, detail in summary['examples'].items()
        },
        'report': str(args.output),
    }, indent=2))
