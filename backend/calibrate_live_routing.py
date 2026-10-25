"""Freeze a train-cohort median for one-at-a-time live PCAT routing.

Offline paper evaluation still ranks the held-out cohort directly. A live
examinee has no concurrent cohort, so the training median is a proxy.
"""

import hashlib
import json
import random
from pathlib import Path

import pandas as pd
import torch

from dataset.adaptest_dataset import AdapTestDataset
from pcat_server import (
    CKPT_PATH, DATA_DIR, ROUTING_CALIBRATION_PATH, STAGE1_MEDIUM_IDS,
    concept_map, init_ncd_evaluator, total_concepts, total_questions,
)


def main():
    logs = pd.read_csv(Path(DATA_DIR) / 'TotalData.csv', header=None).drop_duplicates()
    students = sorted(int(student) for student in logs[0].unique())
    shuffled = students.copy()
    random.Random(20).shuffle(shuffled)
    train_students = sorted(shuffled[:int(0.8 * len(shuffled))])
    train_set = set(train_students)
    medium_set = set(STAGE1_MEDIUM_IDS)
    triplets = [
        (int(student), int(question), int(correct))
        for student, question, correct in logs.itertuples(index=False, name=None)
        if int(student) in train_set and int(question) in medium_set
    ]
    data = AdapTestDataset(
        triplets, concept_map, max(students) + 1,
        total_questions, total_concepts, 20,
    )
    data.reset2()
    model = init_ncd_evaluator(tau=0.0)
    model.init_model(data)
    model.adaptest_load(CKPT_PATH)
    concepts = sorted({c for q in STAGE1_MEDIUM_IDS for c in concept_map[q]})
    scores = []
    for index, student in enumerate(train_students, start=1):
        for q in STAGE1_MEDIUM_IDS:
            data.apply_selection(student, q)
        model.update(data, sid=student, out=False)
        with torch.no_grad():
            score = torch.sigmoid(model.model.student_emb.weight[student, concepts]).mean().item()
        scores.append(float(score))
        if index % 40 == 0:
            print(f'Calibrated {index}/{len(train_students)} students', flush=True)
    scores.sort()
    middle = len(scores) // 2
    threshold = (scores[middle - 1] + scores[middle]) / 2 if len(scores) % 2 == 0 else scores[middle]
    calibration = {
        'dataset': 'Dense_EdNetTOEIC_Balanced90_90d',
        'seed': 20,
        'cohort': 'training_only',
        'student_count': len(train_students),
        'stage1_medium_10': STAGE1_MEDIUM_IDS,
        'model_sha256': hashlib.sha256(Path(CKPT_PATH).read_bytes()).hexdigest(),
        'training_median_mastery': threshold,
        'method': 'individual 10-epoch NCD adaptation, tau=0; mean sigmoid mastery on medium-paper concepts',
    }
    Path(ROUTING_CALIBRATION_PATH).write_text(json.dumps(calibration, indent=2), encoding='utf-8')
    print(f'Routing threshold: {threshold:.6f}', flush=True)


if __name__ == '__main__':
    main()
