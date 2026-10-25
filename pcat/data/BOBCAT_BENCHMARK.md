# BOBCAT comparison on EdNet

`scripts/run_code/run_bobcat_comparison.py` adds an item-level BOBCAT baseline to
the completed TOEIC-adapted PCAT experiment. It reuses the five NCD checkpoints
and selected PCAT papers; it does not rerun NSGA-II or overwrite its results.

From the workspace root:

```powershell
.\pcat\.venv\Scripts\python.exe pcat/scripts/run_code/run_bobcat_comparison.py
```

Defaults: seeds 20–24, 100 policy-training epochs per seed, batch size 16,
20 administered items, one CPU thread. Small batches are necessary on the
current 8-GB Windows machine because bilevel training retains second-order
gradient graphs. A one-epoch smoke run took about 10 seconds of training;
the full five-seed run may take roughly 1.5 hours depending on machine load.

The separate progress file is `scripts/run_code/bobcat_full_status.json`.
Each seed's checkpoint is `model/ckpt/bobcat_<dataset>_full_seed<seed>.pt`.
Checkpoints include the auxiliary learner, policy, optimizers, learned initial
mastery, RNG states, epoch and provenance hashes. They are saved every five
epochs and at the final epoch. Repeating the command resumes saved training;
data, settings or source mismatches fail explicitly. Final and partial results
are written to a separate `*_bobcat_full_100epochs_seeds20-21-22-23-24_comparison_results.json`.

Windows can briefly deny replacement of files watched by other processes. File
writes and replacements now retry permission failures for up to five seconds;
a persistent status-file failure produces a warning without stopping training.
Checkpoint and result-write failures still fail explicitly to avoid claiming
unsaved work is durable. The first full run stopped after epoch 14 on a status
rename error. Its epoch-10 checkpoint was backed up and migrated solely to the
new runner-source hash after verifying that all training state, data, NCD and
PCAT reference hashes were unchanged. `scripts/run_code/bobcat_io_recovery.json`
records this one-time recovery; training resumes with epoch 11.

## Method and source

The implementation uses the straight-through (biased gradient) BOBCAT variant:

- [Original BOBCAT implementation](https://github.com/arghosh/BOBCAT), especially
  the `pick_biased_samples`, `inner_algo` and `run_biased` training routines.
- [PCAT authors' implementation](https://github.com/ECNU-ILOG/PCAT), whose local
  `scripts/bobcat_train.py` supplies the NCD auxiliary meta-learner and bilevel
  updates, and whose `model/utils.py` supplies the 256-unit policy network.

The auxiliary model and initial mastery are jointly learned with the selection
policy. This auxiliary learner is not the final NCD scorer. Final diagnosis
uses exactly the existing PCAT NCD model and observed-answer update settings.
This isolates comparison of selection policies; it is not a reproduction of
BOBCAT's original datasets or its standalone end-to-end prediction benchmark.

Two correctness repairs were necessary in `bobcat_train.py`: flatten batched
action indices before updating each learner's availability mask (matching the
original BOBCAT actor's action shape), and retain the batch dimension when the
auxiliary model receives a one-learner batch. The old standalone training entry
point is commented out; this new runner supplies the EdNet training loop.

Hyperparameters are fixed before the full run: model Adam LR 1e-4, prior SGD LR
1e-4, policy Adam LR 2e-3, inner LR 0.1 and five inner gradient steps. These follow
the local BOBCAT defaults. The final epoch is used; there is no test-set tuning
or selection of the epoch with the best test result. This is a baseline run
with fixed hyperparameters, not evidence of optimally tuned BOBCAT performance.

## Evaluation protocol

- Reproduce each PCAT seed's exact shuffled 80/20 learner split: 242 train,
  61 test. Only outer-training learners enter policy training.
- Within each training learner, deterministically reserve 18 of the 90 items
  as policy-training query targets; the other 72 form the selectable support
  pool. The policy selects 20 support items. The support/query partition is
  independently seeded per learner and fixed during training. These are inner
  training tasks, not the outer held-out test learners.
- At test time, all 90 items are candidates. Policy inputs start at zero;
  a selected answer is revealed only after its action is finalized. Policy
  weights never change on test learners.
- The final scorer uses the existing per-seed NCD checkpoint, ten adaptation
  epochs, batch 64 and no shrinkage. AUC/ACC use each learner's 70 unadministered
  items; the actual query items can differ between methods.
- COV and EXP use the same Q-matrix and original EdNet exposure rates as PCAT.
- Replay PCAT and Fixed and require their AUC/ACC/COV/EXP to match saved results
  within 1e-7. The full run fails rather than silently comparing incompatible
  checkpoints or scoring settings.

The four reported methods are:

| Method | Selection | Bundle constraint |
| --- | --- | --- |
| PCAT | Saved medium paper, mastery-routed easy/hard branch | Whole bundles |
| Fixed_medium_easy | Saved PCAT medium+easy, same for everyone | Whole bundles |
| BOBCAT_ST | Learned policy chooses one item at a time | None |
| Random_item | Uniform sampling of 20 distinct items per learner | None |

`Random_item` averages three repetitions within each split before reporting the
five-split mean and population standard deviation. It is different from the
older random-paper baseline, which assembled three levels and used medium+easy.
Fixed is an ablation of the PCAT-selected paper, not a separately optimized
fixed-form competitor. The previous results remain in their original files.

## Bundle and timing interpretation

`broken_bundle_test_rate` is the fraction of learners whose selected questions
include at least one incomplete multi-item bundle. `incomplete_bundle_rate` is
the fraction of touched multi-item bundles that are incomplete, pooled over
learners. Untouched bundles and singleton items do not inflate the denominator.
Selecting a partial bundle is a violation of this project's whole-bundle
requirement; it does not establish that the chosen item is unanswerable when
its passage/audio is presented.

Constraints differ between PCAT and unconstrained item-level BOBCAT. The
comparison measures the tradeoff; it cannot establish superiority under equal
bundle constraints. A future constrained CAT baseline would address that gap.

Timing reports CPU wall time for the entire 61-learner cohort, separating
selection/routing from final NCD diagnosis, and excludes model loading. BOBCAT
policy calls are batched across simulated learners. There is no real exam UI,
audio playback or network latency. Consequently these times are not per-user
production latency and should not be described as proof that PCAT is faster.

## Verification

```powershell
.\pcat\.venv\Scripts\python.exe pcat/scripts/run_code/test_bobcat_comparison.py
```

Behavioral tests cover exact/disjoint student splits, masked/disjoint inner
support/query labels, independent action masks across learners, invariance of
test selections to changes in unobserved labels, bundle metrics, actual policy
learning, and bit-identical policy weights after checkpoint resume. A one-epoch
smoke run additionally verified the shared evaluator against saved seed-20 PCAT
and Fixed results. Smoke scores must not be presented as trained BOBCAT results.
