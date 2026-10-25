"""Track the long CPU PCAT run and aggregate its five seed results."""

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATASET = 'Dense_EdNetTOEIC_Balanced90_90d'
SEEDS = (20, 21, 22, 23, 24)
PREFIX = f'{DATASET}_paper_query_100gen_80pop_'
STATUS_PATH = HERE / 'full_100gen_80pop_status.json'
GENERATION = re.compile(r'^\s*(\d+)\s*\|', re.MULTILINE)
RESUMED_GENERATION = re.compile(r'Resuming NSGA-II seed \d+ after generation (\d+)')


def result_path(seed):
    return HERE / f'{PREFIX}seeds{seed}_benchmark_evaluation_results.json'


def update_status(state, error=None):
    progress = {}
    for seed in SEEDS:
        stdout = HERE / f'full_100gen_80pop_seed{seed}.stdout.log'
        stderr = HERE / f'full_100gen_80pop_seed{seed}.stderr.log'
        output = stdout.read_text(encoding='utf-8', errors='replace') if stdout.exists() else ''
        problems = stderr.read_text(encoding='utf-8', errors='replace') if stderr.exists() else ''
        generations = GENERATION.findall(output)
        resumed = RESUMED_GENERATION.findall(output)
        progress[str(seed)] = {
            'last_completed_generation': max(
                int(generations[-1]) if generations else 0,
                int(resumed[-1]) if resumed else 0,
            ),
            'result_ready': result_path(seed).exists(),
            'stderr_tail': problems[-800:] if problems else '',
        }
    status = {
        'state': state,
        'updated_utc': datetime.now(timezone.utc).isoformat(),
        'configuration': {'generations': 100, 'population': 80, 'offspring': 50, 'seeds': SEEDS},
        'progress': progress,
    }
    if error:
        status['error'] = error
    STATUS_PATH.write_text(json.dumps(status, indent=2), encoding='utf-8')
    return status


def main():
    for _ in range(24 * 60):
        status = update_status('running')
        if any('Traceback (most recent call last)' in item['stderr_tail'] for item in status['progress'].values()):
            update_status('failed', 'A seed process wrote a Python traceback; inspect its stderr log.')
            return 1
        if all(item['result_ready'] for item in status['progress'].values()):
            completed = subprocess.run(
                [sys.executable, str(HERE / 'aggregate_seed_results.py')],
                cwd=HERE, capture_output=True, text=True, check=False,
            )
            if completed.returncode == 0:
                update_status('complete')
                return 0
            update_status('waiting_for_valid_results', completed.stderr[-800:])
        time.sleep(60)
    update_status('timed_out', 'The five runs did not finish within 24 hours.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
