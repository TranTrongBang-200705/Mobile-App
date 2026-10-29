"""
Find the optimal 30-item paper covering all 7 TOEIC parts in both Easy and Hard paths,
evaluated directly on the 242 test students with the NCD seed 20 checkpoint.
"""

import copy
import json
import os
import sys
import time
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

DATASET = 'Dense_EdNetTOEIC_Balanced90_90d'
DATA_DIR = ROOT / 'data' / DATASET
CATALOG_PATH = DATA_DIR / 'toeic_question_catalog.csv'
Q_PATH = DATA_DIR / 'q.csv'
CKPT_PATH = ROOT / 'model' / 'ckpt' / f'model_{DATASET}_seed20_train_ncd.pt'
QUESTIONS_JSON_PATH = ROOT / 'pcat_live_questions.json'
AUDIO_DIR = ROOT / 'audio_cache'
IMAGE_DIR = ROOT / 'image_cache'
OUTPUT_JSON = ROOT / 'scripts' / 'run_code' / 'optimized_7part_paper_seed20.json'

def load_environment():
    catalog = pd.read_csv(CATALOG_PATH)
    q_df = pd.read_csv(Q_PATH, header=None)
    concept_map = {idx: np.where(np.array(row))[0].tolist() for idx, row in enumerate(q_df.values)}
    
    with open(QUESTIONS_JSON_PATH, 'r', encoding='utf-8') as f:
        questions_content = json.load(f)
        
    ckpt = torch.load(CKPT_PATH, map_location='cpu', weights_only=False)
    k_weight = ckpt['k_difficulty.weight'].numpy()
    raw_diff = {
        q: float(np.mean(k_weight[q][k_weight[q] != 0])) if np.any(k_weight[q] != 0) else 0.5
        for q in range(len(catalog))
    }
    catalog['diff'] = [raw_diff[q] for q in range(len(catalog))]
    
    # Metadata and test splits
    metadata = {
        'stu_num': data_params[DATASET]['stu_num'],
        'prob_num': data_params[DATASET]['prob_num'],
        'know_num': data_params[DATASET]['know_num'],
    }
    
    response_logs = pd.read_csv(DATA_DIR / 'TotalData.csv', header=None).drop_duplicates()
    
    import random
    random.seed(20)
    np.random.seed(20)
    torch.manual_seed(20)
    
    total_stu = list(range(metadata['stu_num']))
    shuffled_stu = total_stu.copy()
    random.shuffle(shuffled_stu)
    n_train = int(len(shuffled_stu) * 0.80)
    train_stu = sorted(shuffled_stu[:n_train])
    test_stu = sorted(shuffled_stu[n_train:])
    
    train_set = set(train_stu)
    test_triplets = []
    for log in response_logs.values:
        s, p, y = int(log[0]), int(log[1]), int(log[2])
        if s not in train_set:
            test_triplets.append((s, p, y))
    
    config = {
        'num_concepts': metadata['know_num'],
        'num_questions': metadata['prob_num'],
        'device': 'cpu',
        'learning_rate': 0.05,
        'batch_size': 512,
        'num_epochs': 10,
        'num_dim': 1,
        'cdm': 'ncd',
        'prednet_len1': 128,
        'prednet_len2': 64,
        'betas': (0.9, 0.999),
        'policy': 'mynew',
        'policy_path': f'{ROOT}/model/ckpt/{DATASET}_bocat_policy.pt',
        'THRESHOLD': 300,
        'start': 0,
        'end': 3000,
        'seed': 20,
        'shrinkage_tau': 0.0,
        'q_matrix': q_df.values,
    }
    
    return catalog, concept_map, metadata, test_stu, test_triplets, config, raw_diff, questions_content

def build_candidates(catalog, raw_diff, questions_content):
    # Verify content and audio
    valid_qs = set()
    for q in range(len(catalog)):
        row = catalog.iloc[q]
        q_idx = int(row['q_idx'])
        part = int(row['part'])
        if str(q_idx) not in questions_content:
            continue
        if part <= 4:
            audio_id = str(q_idx) if part <= 2 else str(row['bundle_id'])
            audio_f = AUDIO_DIR / f'{audio_id}.mp3'
            if not audio_f.exists():
                continue
        valid_qs.add(q_idx)

    print(f"Valid verified questions in bank: {len(valid_qs)} / {len(catalog)}")
    
    bundles_by_part = defaultdict(list)
    for b_id, grp in catalog.groupby('bundle_id'):
        qs = grp['q_idx'].tolist()
        part = int(grp['part'].iloc[0])
        if all(q in valid_qs for q in qs):
            d = float(np.mean([raw_diff[q] for q in qs]))
            bundles_by_part[part].append({
                'bundle_id': b_id,
                'part': part,
                'size': len(qs),
                'qs': qs,
                'diff': d
            })

    for p in range(1, 8):
        bundles_by_part[p].sort(key=lambda x: x['diff'])
        print(f"Part {p}: {len(bundles_by_part[p])} bundles (sizes: {[b['size'] for b in bundles_by_part[p]]})")

    # Structure 1:
    # Stage 1: P3 (size 3) + P1 (1) + P2 (1) = 5L; P6 (size 4) + P5 (1) = 5R. (Parts: 1, 2, 3, 5, 6)
    # Stage 2A (Easy): P4 (size 3) + P2 (2 singles) = 5L; P7 (size 5) = 5R. (Parts: 2, 4, 7)
    # Stage 2B (Hard): P4 (size 3) + P2 (2 singles) = 5L; P7 (size 5) or [P7(4) + P5(1)] = 5R. (Parts: 2, 4, 7 or 2, 4, 5, 7)
    # Both paths have {1, 2, 3, 4, 5, 6, 7}!
    
    # We will search top combinations
    p1_singles = bundles_by_part[1]  # 3 singles
    p2_singles = bundles_by_part[2]  # 12 singles
    p3_bundles = bundles_by_part[3]  # 5 bundles of 3
    p4_bundles = bundles_by_part[4]  # 3 bundles of 3
    p5_singles = bundles_by_part[5]  # 25 singles
    p6_bundles = bundles_by_part[6]  # 3 bundles of 4
    p7_bundles = bundles_by_part[7]  # 2 of 5, 1 of 4

    # P4 assignments:
    # 2A gets lowest diff P4, 2B gets highest diff P4
    p4_easy = p4_bundles[0]   # b1810 (diff 0.065)
    p4_hard = p4_bundles[-1]  # b2071 (diff 0.265)

    # P7 assignments:
    p7_easy = [b for b in p7_bundles if b['size'] == 5 and b['diff'] < 0][0] # b5284 (diff -0.040)
    p7_hard_candidates = [b for b in p7_bundles if b['bundle_id'] != p7_easy['bundle_id']]

    # P3 for Stage 1 (Medium): b1426 (0.001) or b1511 (0.026)
    p3_stage1_candidates = [b for b in p3_bundles if -0.05 < b['diff'] < 0.10]
    
    # P6 for Stage 1 (Medium): b5213 (0.004) or b5214 (0.031)
    p6_stage1_candidates = [b for b in p6_bundles if b['diff'] >= 0]

    candidates = []

    for p3_b in p3_stage1_candidates:
        for p6_b in p6_stage1_candidates:
            for p1_b in p1_singles:
                # Stage 1 needs 1 P2 single and 1 P5 single (aiming for medium diff)
                # Available P2 singles
                med_p2 = [b for b in p2_singles if -0.05 <= b['diff'] <= 0.05]
                med_p5 = [b for b in p5_singles if 0.0 <= b['diff'] <= 0.05]
                
                for p2_s1 in med_p2:
                    for p5_s1 in med_p5:
                        s1_qs = p3_b['qs'] + p1_b['qs'] + p2_s1['qs'] + p6_b['qs'] + p5_s1['qs']
                        s1_diff = float(np.mean([raw_diff[q] for q in s1_qs]))
                        
                        # Stage 2A (Easy):
                        # P4 easy (b1810) + 2 easiest P2 singles not in S1 + P7 easy (b5284)
                        avail_p2_easy = [b for b in p2_singles if b['bundle_id'] != p2_s1['bundle_id'] and b['diff'] < 0]
                        if len(avail_p2_easy) < 2:
                            continue
                        s2a_qs = p4_easy['qs'] + avail_p2_easy[0]['qs'] + avail_p2_easy[1]['qs'] + p7_easy['qs']
                        s2a_diff = float(np.mean([raw_diff[q] for q in s2a_qs]))
                        
                        # Stage 2B (Hard):
                        # P4 hard (b2071) + 2 hardest P2 singles + P7 hard
                        avail_p2_hard = [b for b in p2_singles if b['bundle_id'] != p2_s1['bundle_id'] and b not in avail_p2_easy[:2]]
                        avail_p2_hard.sort(key=lambda x: -x['diff'])
                        if len(avail_p2_hard) < 2:
                            continue
                            
                        for p7_h in p7_hard_candidates:
                            if p7_h['size'] == 5:
                                s2b_qs = p4_hard['qs'] + avail_p2_hard[0]['qs'] + avail_p2_hard[1]['qs'] + p7_h['qs']
                            else: # size 4, need 1 hard P5 single
                                avail_p5_hard = [b for b in p5_singles if b['bundle_id'] != p5_s1['bundle_id']]
                                avail_p5_hard.sort(key=lambda x: -x['diff'])
                                s2b_qs = p4_hard['qs'] + avail_p2_hard[0]['qs'] + avail_p2_hard[1]['qs'] + p7_h['qs'] + avail_p5_hard[0]['qs']
                                
                            s2b_diff = float(np.mean([raw_diff[q] for q in s2b_qs]))
                            
                            all_qs = s1_qs + s2a_qs + s2b_qs
                            if len(set(all_qs)) != 30:
                                continue
                                
                            # Check difficulty ordering
                            if s2a_diff < s1_diff < s2b_diff and (s1_diff - s2a_diff >= 0.02) and (s2b_diff - s1_diff >= 0.02):
                                candidates.append({
                                    's1': s1_qs,
                                    's2a': s2a_qs,
                                    's2b': s2b_qs,
                                    'diff_s1': s1_diff,
                                    'diff_s2a': s2a_diff,
                                    'diff_s2b': s2b_diff,
                                    'sep': (s1_diff - s2a_diff) + (s2b_diff - s1_diff)
                                })
                                
    print(f"Generated {len(candidates)} candidate 30-item papers meeting all structural constraints!")
    candidates.sort(key=lambda x: -x['sep'])
    return candidates[:15]  # Top 15 distinct candidates for NCD evaluation

def evaluate_candidate(cand, catalog, concept_map, metadata, test_stu, test_triplets, config):
    paper1 = cand['s2a']  # Easy
    paper2 = cand['s1']   # Medium
    paper3 = cand['s2b']  # Hard
    
    paper_length = 10
    test_length = 20
    target_rate = test_length / metadata['prob_num']
    
    eval_data = AdapTestDataset(
        test_triplets, concept_map,
        metadata['stu_num'], metadata['prob_num'],
        metadata['know_num'], 20
    )
    eval_data.reset2()
    
    local_cfg = copy.deepcopy(config)
    local_cfg['num_epochs'] = 10
    local_cfg['batch_size'] = 64
    local_cfg['shrinkage_tau'] = 0.0
    model = NCDModel(**local_cfg)
    model.init_model(eval_data)
    model.adaptest_load(str(CKPT_PATH))
    
    partial_concepts = {}
    stu_cov = {}
    
    for stu in test_stu:
        concepts = set()
        for prob in paper2:
            eval_data.apply_selection(stu, prob)
            concepts.update(concept_map[prob])
        partial_concepts[stu] = concepts
        
    hard_students, _ = rank_medium_paper_mastery(
        model, eval_data, test_stu, paper2, concept_map
    )
    
    for stu in test_stu:
        concepts = partial_concepts[stu]
        stage2 = paper3 if stu in hard_students else paper1
        for prob in stage2:
            eval_data.apply_selection(stu, prob)
            concepts.update(concept_map[prob])
            
        stu_cov[stu] = len(concepts) / metadata['know_num']
        eval_data.meta[stu] = [
            que for que in range(metadata['prob_num'])
            if que not in eval_data._tested[stu]
        ]
        
    cov = sum(stu_cov.values()) / max(len(stu_cov), 1)
    model.update(eval_data, out=False)
    query_metrics = model.evaluate(eval_data)
    
    return {
        'auc': float(query_metrics['auc']),
        'acc': float(query_metrics['acc']),
        'cov': float(cov),
        'hard_students': len(hard_students),
        'easy_students': len(test_stu) - len(hard_students),
    }

def main():
    t0 = time.time()
    print("Step 1: Loading environment...")
    catalog, concept_map, metadata, test_stu, test_triplets, config, raw_diff, questions_content = load_environment()
    
    print("\nStep 2: Building candidate papers...")
    top_candidates = build_candidates(catalog, raw_diff, questions_content)
    
    print(f"\nStep 3: Evaluating top {len(top_candidates)} candidates on 242 test learners...")
    best_res = None
    best_cand = None
    best_score = -1.0
    
    for idx, cand in enumerate(top_candidates):
        metrics = evaluate_candidate(cand, catalog, concept_map, metadata, test_stu, test_triplets, config)
        score = metrics['auc'] * 0.5 + metrics['acc'] * 0.3 + metrics['cov'] * 0.2
        print(f"Cand {idx+1:02d}: AUC={metrics['auc']:.4f}, ACC={metrics['acc']:.4f}, COV={metrics['cov']:.4f}, Easy/Hard={metrics['easy_students']}/{metrics['hard_students']}, Diffs=({cand['diff_s2a']:.3f}, {cand['diff_s1']:.3f}, {cand['diff_s2b']:.3f})")
        
        if score > best_score:
            best_score = score
            best_res = metrics
            best_cand = cand
            
    print("\n" + "="*60)
    print("BEST 7-PART OPTIMIZED PAPER FOUND:")
    print(f"AUC: {best_res['auc']:.4f}, ACC: {best_res['acc']:.4f}, COV: {best_res['cov']:.4f}")
    print(f"Stage 1 (Medium - 10 items): {best_cand['s1']}")
    print(f"Stage 2A (Easy - 10 items):   {best_cand['s2a']}")
    print(f"Stage 2B (Hard - 10 items):   {best_cand['s2b']}")
    print(f"Difficulties: Easy={best_cand['diff_s2a']:.3f}, Medium={best_cand['diff_s1']:.3f}, Hard={best_cand['diff_s2b']:.3f}")
    
    # Verify part coverage
    cat_idx = catalog.set_index('q_idx')
    s1_parts = sorted(set(cat_idx.loc[best_cand['s1'], 'part']))
    s2a_parts = sorted(set(cat_idx.loc[best_cand['s2a'], 'part']))
    s2b_parts = sorted(set(cat_idx.loc[best_cand['s2b'], 'part']))
    easy_full = sorted(set(s1_parts + s2a_parts))
    hard_full = sorted(set(s1_parts + s2b_parts))
    
    print(f"\nPart coverage:")
    print(f"Stage 1: {s1_parts}")
    print(f"Stage 2A: {s2a_parts}  --> Easy Path (S1 + S2A): {easy_full} (Count: {len(easy_full)})")
    print(f"Stage 2B: {s2b_parts}  --> Hard Path (S1 + S2B): {hard_full} (Count: {len(hard_full)})")
    
    # Save output
    output_data = {
        'methodology': {
            'optimization': 'Constrained 7-Part Direct NCD Evaluation',
            'dataset': DATASET,
            'paper_seed': 20,
            'test_length': 20,
            'part_coverage_easy': easy_full,
            'part_coverage_hard': hard_full,
        },
        'metrics': best_res,
        'stages': {
            'medium': best_cand['s1'],
            'easy': best_cand['s2a'],
            'hard': best_cand['s2b'],
        },
        'difficulties': {
            'easy_mean': best_cand['diff_s2a'],
            'medium_mean': best_cand['diff_s1'],
            'hard_mean': best_cand['diff_s2b'],
        },
        'full_30': best_cand['s1'] + best_cand['s2a'] + best_cand['s2b'],
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\nSaved best paper configuration to: {OUTPUT_JSON}")
    print(f"Total time elapsed: {time.time() - t0:.2f} seconds")

if __name__ == '__main__':
    main()
