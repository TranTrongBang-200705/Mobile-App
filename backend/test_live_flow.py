"""Checks for the optimized live paper and its asset readiness gate."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from pcat_server import (
    OPTIMIZED_STAGES, PAPER_ASSET_ISSUES, PAPER_SEED, PAPER_SOURCE,
    QUESTIONS_JSON_PATH, RESULT_PATH, ROUTING_THRESHOLD, SESSIONS,
    DiagnoseRequest, RouteRequest,
    catalog_df, diagnose_full_test, get_stage1_questions, health_check,
    route_stage2,
)


class LiveFlowTest(unittest.TestCase):
    def test_demo_question_bank_is_not_active(self):
        self.assertEqual(Path(QUESTIONS_JSON_PATH).name, 'pcat_live_questions.json')

    def test_optimized_paper_matches_saved_seed_and_constraints(self):
        with open(RESULT_PATH, encoding='utf-8') as source:
            paper = json.load(source)['per_seed_details'][str(PAPER_SEED)]['selected_paper']
        self.assertEqual(OPTIMIZED_STAGES['medium'], paper['stage1_medium_10'])
        self.assertEqual(OPTIMIZED_STAGES['easy'], paper['stage2a_easy_10'])
        self.assertEqual(OPTIMIZED_STAGES['hard'], paper['stage2b_hard_10'])
        self.assertEqual(set(sum(OPTIMIZED_STAGES.values(), [])), set(paper['full_30']))
        catalog = catalog_df.set_index('q_idx')
        for ids in OPTIMIZED_STAGES.values():
            self.assertEqual(len(ids), 10)
            self.assertEqual(sum(int(catalog.loc[q, 'part']) <= 4 for q in ids), 5)

    def test_incomplete_paper_is_not_served(self):
        self.assertIsNotNone(ROUTING_THRESHOLD)
        with patch.dict(PAPER_ASSET_ISSUES, {'content': [4]}, clear=True):
            self.assertEqual(health_check()['paper_source'], PAPER_SOURCE)
            self.assertEqual(health_check()['status'], 'paper_unavailable')
            previous_session_count = len(SESSIONS)
            for action in (
                get_stage1_questions,
                lambda: route_stage2(RouteRequest(session_id='none', stage1_answers=[])),
                lambda: diagnose_full_test(DiagnoseRequest(session_id='none', all_answers=[])),
            ):
                with self.assertRaises(HTTPException) as error:
                    action()
                self.assertEqual(error.exception.status_code, 503)
            self.assertEqual(len(SESSIONS), previous_session_count)


if __name__ == '__main__':
    unittest.main()
