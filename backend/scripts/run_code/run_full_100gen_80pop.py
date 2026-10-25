"""Run and resume the five full PCAT seeds with at most two CPU workers."""

import ctypes
import os
import subprocess
import sys
import time

from monitor_full_run import HERE, SEEDS, result_path, update_status


def run_seeds():
    pending = [seed for seed in SEEDS if not result_path(seed).exists()]
    running = {}
    failed = []
    update_status('running')

    while pending or running:
        while pending and len(running) < 2:
            seed = pending.pop(0)
            stdout = (HERE / f'full_100gen_80pop_seed{seed}.stdout.log').open('w', encoding='utf-8')
            stderr = (HERE / f'full_100gen_80pop_seed{seed}.stderr.log').open('w', encoding='utf-8')
            command = [
                sys.executable, '-u', str(HERE / 'main.py'),
                '--generations', '100', '--population', '80',
                '--offspring', '50', '--seeds', str(seed), '--device', 'cpu',
                '--content-balance', 'none',  # Historical run and checkpoint names.
            ]
            try:
                process = subprocess.Popen(command, cwd=HERE, stdout=stdout, stderr=stderr)
            except Exception:
                stdout.close()
                stderr.close()
                raise
            running[seed] = (process, stdout, stderr)
            print(f'Started seed {seed}, pid={process.pid}', flush=True)

        if running:
            time.sleep(60)
        for seed, (process, stdout, stderr) in list(running.items()):
            code = process.poll()
            if code is None:
                continue
            stdout.close()
            stderr.close()
            del running[seed]
            if code != 0 or not result_path(seed).exists():
                failed.append(seed)
                print(f'Seed {seed} failed with exit code {code}', flush=True)
            else:
                print(f'Seed {seed} completed', flush=True)
        update_status('running')

    if failed:
        update_status('failed', f'Failed seeds: {failed}; inspect their stderr logs.')
        return 1

    completed = subprocess.run(
        [sys.executable, str(HERE / 'aggregate_seed_results.py')],
        cwd=HERE, capture_output=True, text=True, check=False,
    )
    if completed.returncode:
        update_status('failed', completed.stderr[-800:])
        return completed.returncode
    update_status('complete')
    print(completed.stdout.strip(), flush=True)
    return 0


def main():
    # The CPU-intensive run can be longer than the Windows idle-sleep timeout.
    # Keep only the system awake while this runner is active; let the display sleep.
    kernel = None
    if os.name == 'nt':
        kernel = ctypes.windll.kernel32
        kernel.SetThreadExecutionState.argtypes = [ctypes.c_uint]
        kernel.SetThreadExecutionState.restype = ctypes.c_uint
        if not kernel.SetThreadExecutionState(0x80000000 | 0x00000001):
            raise OSError('Could not defer automatic sleep during the PCAT run')
        print('Automatic system sleep deferred while PCAT is running', flush=True)
    try:
        return run_seeds()
    finally:
        if kernel is not None:
            kernel.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    raise SystemExit(main())
