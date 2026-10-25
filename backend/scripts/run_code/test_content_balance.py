"""Structural checks for the TOEIC-specific balanced PCAT paper constraint."""

import sys
import unittest
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from dense_paper import decode_unique_questions, partition_toeic_stages


class ListeningReadingBalanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = ROOT / 'data' / 'Dense_EdNetTOEIC_Balanced90_90d'
        catalog = pd.read_csv(data / 'toeic_question_catalog.csv')
        cls.part_map = dict(zip(catalog.q_idx.astype(int), catalog.part.astype(int)))
        cls.bundle_map = dict(zip(catalog.q_idx.astype(int), catalog.bundle_id.astype(str)))
        cls.q_matrix = pd.read_csv(data / 'q.csv', header=None).to_numpy()
        cls.difficulty = cls.q_matrix * np.linspace(0.2, 0.9, len(cls.q_matrix))[:, None]
        cls.allowed = list(range(len(cls.q_matrix)))
        cls.bundles = defaultdict(set)
        for q, bundle in cls.bundle_map.items():
            cls.bundles[bundle].add(q)

    def assert_valid_paper(self, stages):
        self.assertEqual([len(stage) for stage in stages], [10, 10, 10])
        self.assertEqual(len({q for stage in stages for q in stage}), 30)
        for stage in stages:
            listening = sum(self.part_map[q] in (1, 2, 3, 4) for q in stage)
            reading = sum(self.part_map[q] in (5, 6, 7) for q in stage)
            self.assertEqual((listening, reading), (5, 5))
            for q in stage:
                self.assertTrue(self.bundles[self.bundle_map[q]].issubset(stage))
        for path in (stages[1] + stages[0], stages[1] + stages[2]):
            self.assertEqual(len(path), 20)
            self.assertEqual(sum(self.part_map[q] in (1, 2, 3, 4) for q in path), 10)
        means = [np.mean([np.mean(self.difficulty[q][self.difficulty[q] != 0]) for q in stage])
                 for stage in stages]
        self.assertEqual(means, sorted(means))

    def test_random_candidate_sets_and_repartition_are_valid(self):
        rng = np.random.default_rng(2026)
        for _ in range(50):
            candidates = rng.choice(self.allowed, 30, replace=False).tolist()
            stages = partition_toeic_stages(
                candidates, self.difficulty, self.part_map, self.bundle_map,
                allowed_questions=self.allowed, content_balance=True,
            )
            self.assert_valid_paper(stages)
            again = partition_toeic_stages(
                stages[0] + stages[1] + stages[2], self.difficulty,
                self.part_map, self.bundle_map,
                allowed_questions=self.allowed, content_balance=True,
            )
            self.assertEqual(stages, again)

    def test_chromosome_decoder_produces_valid_both_branches(self):
        question_type = defaultdict(list)
        type_ids = {}
        for q, row in enumerate(self.q_matrix):
            key = tuple(np.flatnonzero(row))
            if key not in type_ids:
                type_ids[key] = len(type_ids)
            question_type[type_ids[key]].append(q)
        chromosome = np.array(
            [i % len(question_type) for i in range(30)] + [0.5] * 30,
            dtype=float,
        )
        paper = decode_unique_questions(
            chromosome, 30, question_type, self.difficulty,
            self.part_map, self.bundle_map, content_balance=True,
        )
        self.assert_valid_paper((paper[:10], paper[10:20], paper[20:]))
        self.assertEqual(
            paper,
            decode_unique_questions(
                chromosome, 30, question_type, self.difficulty,
                self.part_map, self.bundle_map, content_balance=True,
            ),
        )

    def test_missing_catalog_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'metadata'):
            partition_toeic_stages(
                self.allowed[:30], self.difficulty, None, self.bundle_map,
                content_balance=True,
            )

    def test_partial_bundle_in_candidate_pool_is_rejected(self):
        grouped = next(items for items in self.bundles.values() if len(items) > 1)
        allowed = [q for q in self.allowed if q != min(grouped)]
        with self.assertRaisesRegex(ValueError, 'incomplete TOEIC bundle'):
            partition_toeic_stages(
                allowed[:30], self.difficulty, self.part_map, self.bundle_map,
                allowed_questions=allowed, content_balance=True,
            )


if __name__ == '__main__':
    unittest.main()
