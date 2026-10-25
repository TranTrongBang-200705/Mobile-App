"""Behavioral checks for policy masking, label isolation and checkpoint resume."""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import torch

from run_bobcat_comparison import (
    Actor, PolicyTrainDataset, bundle_metrics, policy_rollout,
    split_students, train_policy, write_json, write_status,
)
from bobcat_train import pick_biased_samples


class BobcatChecks(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(17)

    def test_atomic_json_survives_temporary_windows_lock(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'status.json'
            path.write_text('{"epoch": 1}', encoding='utf-8')
            replace = Path.replace
            calls = []

            def temporarily_locked(source, target):
                calls.append(source)
                if len(calls) < 3:
                    self.assertEqual(json.loads(path.read_text())['epoch'], 1)
                    raise PermissionError('simulated Windows sharing conflict')
                return replace(source, target)

            with patch.object(Path, 'replace', temporarily_locked), patch('time.sleep'):
                write_json(path, {'epoch': 2})
            self.assertEqual(json.loads(path.read_text())['epoch'], 2)
            self.assertEqual(len(calls), 3)

    def test_persistent_status_lock_does_not_abort_training(self):
        with patch('run_bobcat_comparison.write_json', side_effect=PermissionError('locked')):
            with patch('sys.stderr'):
                write_status(Path('status.json'), {'state': 'running'})

    def test_split_matches_pcat_and_is_disjoint(self):
        import random
        for seed in range(20, 25):
            expected = list(range(303))
            random.Random(seed).shuffle(expected)
            train, test = split_students(303, seed)
            self.assertEqual(train, sorted(expected[:242]))
            self.assertEqual(test, sorted(expected[242:]))
            self.assertFalse(set(train) & set(test))

    def test_training_support_query_are_disjoint_and_labels_masked(self):
        labels = np.ones((4, 90))
        ds = PolicyTrainDataset(labels, seed=20, test_length=20)
        b = ds.batch
        self.assertTrue(torch.all(b['input_mask'].sum(1) == 72))
        self.assertTrue(torch.all(b['output_mask'].sum(1) == 18))
        self.assertFalse(torch.any(b['input_mask'] * b['output_mask']))
        self.assertFalse(torch.any(b['input_labels'] * b['output_mask']))
        self.assertFalse(torch.any(b['output_labels'] * b['input_mask']))

    def test_batched_actions_do_not_mask_other_students(self):
        class ScriptedPolicy:
            def __init__(self):
                self.step = 0

            def __call__(self, state, available):
                actions = torch.tensor([self.step, 1 - self.step])
                self.step += 1
                mask = torch.zeros_like(state).scatter_(1, actions[:, None], 1)
                return mask, actions[:, None]

        class Env:
            def reset(self, batch):
                return dict(action_mask=batch['input_mask'].clone(),
                            train_mask=torch.zeros_like(batch['input_mask']))

            def step(self, env):
                return env['train_mask']

        batch = dict(input_labels=torch.zeros((2, 3)), input_mask=torch.ones((2, 3)))
        cfg = dict(mode='eval', n_query=2)
        pick_biased_samples(Env(), batch, cfg, SimpleNamespace(policy=ScriptedPolicy()),
                            [torch.zeros((1, 2), requires_grad=True)])
        self.assertTrue(torch.equal(cfg['train_mask'], torch.tensor([[1., 1., 0.], [1., 1., 0.]])))

    def test_test_rollout_cannot_see_unselected_answers(self):
        policy = Actor(12, 12)
        labels = torch.randint(0, 2, (3, 12)).float()
        selected = policy_rollout(policy, labels, 5)
        altered = labels.clone()
        for row, questions in enumerate(selected):
            self.assertEqual(len(set(questions)), 5)
            unseen = [q for q in range(12) if q not in questions]
            altered[row, unseen] = 1 - altered[row, unseen]
        self.assertEqual(policy_rollout(policy, altered, 5), selected)

    def test_bundle_metric_counts_only_touched_multitem_bundles(self):
        bundles = {0: 'a', 1: 'a', 2: 'b', 3: 'b', 4: 'single'}
        metrics = bundle_metrics({0: [0, 1, 4], 1: [2, 4]}, bundles)
        self.assertEqual(metrics['broken_bundle_test_rate'], .5)
        self.assertEqual(metrics['incomplete_bundle_rate'], .5)
        self.assertEqual(metrics['touched_multitem_bundles'], 2)

    def test_bilevel_learning_and_resuming_match_uninterrupted_training(self):
        problem = dict(q=np.tile([[1, 0], [0, 1]], (4, 1)),
                       responses=np.array([[0, 1, 1, 0, 1, 0, 0, 1],
                                           [1, 0, 0, 1, 0, 1, 1, 0]]))
        args = SimpleNamespace(test_length=2, batch_size=2, epochs=2)
        spec = {'test': 'resume'}
        progress = lambda *unused: None
        with tempfile.TemporaryDirectory() as tmp:
            full = Path(tmp) / 'full.pt'
            resumed = Path(tmp) / 'resume.pt'
            policy_full, _, _ = train_policy(problem, [0, 1], 20, args, spec, full, progress)
            args.epochs = 1
            policy_first, history, _ = train_policy(problem, [0, 1], 20, args, spec, resumed, progress)
            before_resume = {k: v.clone() for k, v in policy_first.state_dict().items()}
            self.assertTrue(np.isfinite(history[0]['train_query_bce']))
            args.epochs = 2
            policy_resumed, history, _ = train_policy(problem, [0, 1], 20, args, spec, resumed, progress)
            self.assertEqual([h['epoch'] for h in history], [1, 2])
            self.assertTrue(any(not torch.equal(before_resume[k], v)
                                for k, v in policy_resumed.state_dict().items()))
            for key, value in policy_full.state_dict().items():
                self.assertTrue(torch.equal(value, policy_resumed.state_dict()[key]), key)


if __name__ == '__main__':
    unittest.main()
