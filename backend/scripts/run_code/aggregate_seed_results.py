"""Combine independently run PCAT seeds into one five-repeat benchmark."""

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='Dense_EdNetTOEIC_Balanced90_90d')
    parser.add_argument('--generations', type=int, default=100)
    parser.add_argument('--population', type=int, default=80)
    parser.add_argument('--seeds', default='20,21,22,23,24')
    parser.add_argument('--suffix', default='', help='Run suffix, e.g. _balancedLR')
    args = parser.parse_args()

    seeds = [int(value.strip()) for value in args.seeds.split(',') if value.strip()]
    if len(seeds) < 2 or len(set(seeds)) != len(seeds):
        raise ValueError('Expected at least two distinct seed IDs')

    per_seed = {}
    first = None
    for seed in seeds:
        path = Path(
            f'{args.dataset}_paper_query_{args.generations}gen_'
            f'{args.population}pop_seeds{seed}{args.suffix}_benchmark_evaluation_results.json'
        )
        result = json.loads(path.read_text(encoding='utf-8'))
        if result['seeds_evaluated'] != [seed]:
            raise ValueError(f'{path} contains the wrong seed')
        if result['methodology']['generations'] != args.generations or result['methodology']['population'] != args.population:
            raise ValueError(f'{path} contains the wrong search configuration')
        if args.suffix == '_balancedLR' and result['methodology'].get('content_balance') != '5 Listening + 5 Reading in each 10-item stage':
            raise ValueError(f'{path} is not a balanced Listening/Reading result')
        if first is None:
            first = result
        elif (result['split_ratio'] != first['split_ratio'] or
              result['selectable_candidate_pool_size'] != first['selectable_candidate_pool_size'] or
              result['query_questions_per_learner'] != first['query_questions_per_learner']):
            raise ValueError(f'{path} is not comparable with the first seed')
        per_seed[str(seed)] = result['per_seed_details'][str(seed)]

    methods = per_seed[str(seeds[0])]['methods']
    metrics = ('auc', 'acc', 'cov', 'exp')
    summary = {}
    for method in methods:
        summary[method] = {}
        for metric in metrics:
            values = [per_seed[str(seed)]['methods'][method][metric] for seed in seeds]
            summary[method][f'{metric}_mean'] = round(mean(values), 4)
            summary[method][f'{metric}_std'] = round(pstdev(values), 4)

    combined = {
        'seeds_evaluated': seeds,
        'split_ratio': first['split_ratio'],
        'methodology': first['methodology'],
        'query_questions_per_learner': first['query_questions_per_learner'],
        'selectable_candidate_pool_size': first['selectable_candidate_pool_size'],
        'multi_seed_summary_mean_std': summary,
        'per_seed_details': per_seed,
    }
    seed_tag = '-'.join(map(str, seeds))
    output = Path(
        f'{args.dataset}_paper_query_{args.generations}gen_'
        f'{args.population}pop_seeds{seed_tag}{args.suffix}_benchmark_evaluation_results.json'
    )
    output.write_text(json.dumps(combined, indent=2), encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
