"""Run and resume balanced PCAT seeds with a configurable worker limit."""

import ctypes
import json
import os
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
STATUS = HERE / 'full_100gen_80pop_balancedLR_status.json'
MAX_WORKERS = int(os.environ.get('PCAT_BALANCED_WORKERS', '1'))
if MAX_WORKERS not in (1, 2):
    raise ValueError('PCAT_BALANCED_WORKERS must be 1 or 2')
GENERATION = re.compile(r'^\s*(\d+)\s*\|', re.MULTILINE)
RESUMED = re.compile(r'Resuming NSGA-II seed \d+ after generation (\d+)')


def enough_memory_for_second_worker():
    """Leave headroom for a second NCD worker on the 8 GB Windows host."""
    if os.name != 'nt':
        return True

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ('length', ctypes.c_uint32), ('memory_load', ctypes.c_uint32),
            ('total_physical', ctypes.c_uint64), ('available_physical', ctypes.c_uint64),
            ('total_pagefile', ctypes.c_uint64), ('available_pagefile', ctypes.c_uint64),
            ('total_virtual', ctypes.c_uint64), ('available_virtual', ctypes.c_uint64),
            ('available_extended_virtual', ctypes.c_uint64),
        ]

    memory = MemoryStatus()
    memory.length = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        return False
    gib = 1024 ** 3
    return memory.available_physical >= 1.25 * gib and memory.available_pagefile >= 2 * gib


def result_path(seed):
    return HERE / f'{PREFIX}seeds{seed}_balancedLR_benchmark_evaluation_results.json'


def update_status(state, error=None):
    progress = {}
    for seed in SEEDS:
        stdout = HERE / f'balancedLR_seed{seed}.stdout.log'
        stderr = HERE / f'balancedLR_seed{seed}.stderr.log'
        output = stdout.read_text(encoding='utf-8', errors='replace') if stdout.exists() else ''
        problems = stderr.read_text(encoding='utf-8', errors='replace') if stderr.exists() else ''
        generations = GENERATION.findall(output)
        resumed = RESUMED.findall(output)
        progress[str(seed)] = {
            'last_completed_generation': max(
                int(generations[-1]) if generations else 0,
                int(resumed[-1]) if resumed else 0,
            ),
            'result_ready': result_path(seed).exists(),
            'stderr_tail': problems[-800:],
        }
    status = {
        'state': state,
        'updated_utc': datetime.now(timezone.utc).isoformat(),
        'configuration': {
            'dataset': DATASET, 'generations': 100, 'population': 80,
            'offspring': 50, 'seeds': SEEDS, 'content_balance': 'listening_reading',
            'max_workers': MAX_WORKERS,
        },
        'progress': progress,
    }
    if error:
        status['error'] = error
    STATUS.write_text(json.dumps(status, indent=2), encoding='utf-8')


def run_seeds():
    pending = [seed for seed in SEEDS if not result_path(seed).exists()]
    running = {}
    update_status('running')
    while pending or running:
        while pending and len(running) < MAX_WORKERS:
            if running and not enough_memory_for_second_worker():
                break
            seed = pending.pop(0)
            stdout = (HERE / f'balancedLR_seed{seed}.stdout.log').open('w', encoding='utf-8')
            stderr = (HERE / f'balancedLR_seed{seed}.stderr.log').open('w', encoding='utf-8')
            command = [
                sys.executable, '-u', str(HERE / 'main.py'),
                '--generations', '100', '--population', '80',
                '--offspring', '50', '--seeds', str(seed), '--device', 'cpu',
                '--content-balance', 'listening_reading',
            ]
            try:
                process = subprocess.Popen(command, cwd=HERE, stdout=stdout, stderr=stderr)
            except Exception:
                stdout.close()
                stderr.close()
                raise
            running[seed] = (process, stdout, stderr)
            print(f'Started balanced seed {seed}, pid={process.pid}', flush=True)
        if running:
            time.sleep(30)
        for seed, (process, stdout, stderr) in list(running.items()):
            code = process.poll()
            if code is None:
                continue
            stdout.close()
            stderr.close()
            del running[seed]
            if code != 0 or not result_path(seed).exists():
                print(f'Seed {seed} failed with exit code {code}', flush=True)
                update_status('failed', f'Seed {seed} failed; inspect its stderr log.')
                return 1
            else:
                print(f'Seed {seed} completed', flush=True)
        update_status('running')
    completed = subprocess.run(
        [sys.executable, str(HERE / 'aggregate_seed_results.py'), '--suffix', '_balancedLR'],
        cwd=HERE, capture_output=True, text=True, check=False,
    )
    if completed.returncode:
        update_status('failed', completed.stderr[-800:])
        return completed.returncode
    update_status('complete')
    print(completed.stdout.strip(), flush=True)
    return 0


def main():
    kernel = None
    if os.name == 'nt':
        kernel = ctypes.windll.kernel32
        kernel.SetThreadExecutionState.argtypes = [ctypes.c_uint]
        kernel.SetThreadExecutionState.restype = ctypes.c_uint
        if not kernel.SetThreadExecutionState(0x80000000 | 0x00000001):
            raise OSError('Could not defer automatic sleep during the balanced PCAT run')
    try:
        return run_seeds()
    finally:
        if kernel is not None:
            kernel.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    raise SystemExit(main())
