# EdNet KT1 cohorts for PCAT

The former `Dense_EdNetTOEIC` benchmark contains 179 learners and 94 questions. The default PCAT dataset is now `Dense_EdNetTOEIC_Balanced90_90d`. This work independently scanned the [EdNet KT1 Parquet mirror](https://huggingface.co/datasets/mgor/EDNet), whose schema and question metadata follow the [Riiid EdNet release](https://github.com/riiid/ednet). The scan read 95,292,768 answer rows from 784,301 learners in 11 shards. It matched all 16,826 rows of the old local subset exactly by learner, question, timestamp, answer, solving ID, and elapsed time. The mirror is a third-party copy and has slightly fewer rows than the count in Riiid's documentation, so its shard hashes are recorded in `scratch/ednet_reselection/scan_manifest.json`.

The selection algorithm uses only question presence, official Part/bundle metadata, and timestamps. It does not use correctness to choose learners or questions. It keeps entire multi-question bundles, requires a complete learner × question matrix, and uses each learner's **first recorded attempt** at each question. The balanced 90-item bank was found by a greedy multi-start search; it is the best reviewed candidate from this search, not a claim of a global mathematical optimum.

| Cohort | Learners | Questions | Part 5 | Parts covered | Median answer span |
| --- | ---: | ---: | ---: | --- | ---: |
| Original `Dense_EdNetTOEIC` | 179 | 94 | 75 | 1, 3, 4, 5, 7 | 186.1 days |
| `Dense_EdNetTOEIC_Full94` | 2,063 | 94 | 75 | 1, 3, 4, 5, 7 | 130.2 days |
| `Dense_EdNetTOEIC_Balanced90` | 1,008 | 90 | 25 | 1–7 | 169.6 days |
| `Dense_EdNetTOEIC_Balanced90_90d` | 303 | 90 | 25 | 1–7 | 47.1 days |

The 90-day cohort is the **default PCAT experiment**: it keeps all seven Parts, has more learners than the original subset, and limits the interval over which the selected answers were given. The full 1,008-learner balanced cohort tests whether conclusions hold with more data. The 2,063-learner Full94 cohort isolates the effect of increasing sample size while keeping the original question bank. Even 90 days is not one exam sitting; the data support an offline simulation, not a claim about actual TOEIC exam scores.

The old subset contains later attempts: among the same 179 learners and 94 questions, replacing its records with first attempts changes 18.2% of correctness labels. Their positive-response rate changes from 58.17% to 42.67%. Existing AUC/ACC results from the old subset must therefore be treated as a separate experiment and cannot be copied over to any new cohort. See `scratch/ednet_reselection/cohort_comparison.json` for the complete comparison.

The balanced bank has 90 questions. An earlier export also included an auxiliary fixed 20-item evaluation subset selected by integer optimization; the current paper-style experiment does not use that subset or exclude its questions from paper assembly. All 90 questions are candidates. After a student answers 20 questions, that student's other 70 questions form the query set for AUC and ACC, as in the authors' published implementation. Item exposure rates come from the full mirror's unique learner-question counts rather than the selected dense cohort, whose items all have exposure 100% by construction.

From the workspace root, regenerate and validate the data with:

```powershell
python pcat/data/reselect_ednet_kt1.py scan
python pcat/data/optimize_ednet_cohort.py --seed-count 4 --candidates-per-part 30
python pcat/data/export_ednet_cohorts.py --balanced-index 2
python pcat/data/derive_time_window_cohort.py --max-days 90
python pcat/data/compare_ednet_cohorts.py
python pcat/data/validate_reselected_ednet.py
```

The first and third commands transfer about 1.88 GB each, one temporary ~171 MB shard at a time. Filtering needs pandas, NumPy, PyArrow, SciPy, and requests. It does not need PyTorch. On this Windows Python 3.14 machine, the benchmark was run with CPU PyTorch 2.14.1, pymoo 0.6.2, and tqdm 4.70.1 in `pcat/.venv` (with system site packages). These versions differ from the paper's older `requirements.txt` pins, which do not support Python 3.14. To rerun from the workspace root:

```powershell
cd pcat/scripts/run_code
..\..\.venv\Scripts\python.exe main.py --test_length 20 --device cpu
```

The default TOEIC adaptation follows the main workflow in Section 4.2 and Algorithm 1 of the supplied PDF (`C:\Users\bangt\Downloads\3711896.3737073.pdf`, [published paper](https://doi.org/10.1145/3711896.3737073)): after the medium paper, NCD estimates each examinee's mastery from those answers alone; the top half of the cohort receives the hard paper and the bottom half the easy paper. This uses the mean NCD mastery over concepts assessed by the medium paper, with student ID breaking exact ties. The PDF prescribes a mastery ranking but does not define a scalar aggregation of its multidimensional mastery vector or a tie rule; these choices make the TOEIC adaptation reproducible. Search optimizes AUC, ACC, COV and EXP, uses 80% training and 20% testing students, and selects the final Pareto paper by training AUC + ACC. Defaults match the paper's 100 NSGA-II generations, population 80 and five repetitions; the author's published code uses 50 offspring.

Whole TOEIC bundles, Q-matrix tags, and the EdNet cohort are adaptations for this project. Each chromosome type now represents exactly one Q-matrix attribute combination, while decoding can still repeat types when completing an indivisible TOEIC bundle; this is a remaining difference from the paper's unique-type solution constraint. The three resulting papers are named by their measured average NCD difficulty, so easy <= medium <= hard. Fitness and test evaluation use the same NCD adaptation settings (10 epochs, batch size 64), and mutation is restricted to the range of actual item difficulties. The current evaluation uses each student's unadministered questions, without a global fixed query set.

The full TOEIC-adapted run completed with 100 NSGA-II generations, population 80, 50 offspring, and five seeds (20–24). Each split had 242 training and 61 test learners; each test learner answered 20 questions and was evaluated on the other 70. The numbers below are test-set mean ± population standard deviation across seeds:

| Method | Query AUC | Query ACC | COV | EXP (lower is better) |
| --- | ---: | ---: | ---: | ---: |
| Random 20-item selection + NCD | 0.7020 ± 0.0098 | 0.6570 ± 0.0060 | 0.6417 ± 0.0565 | 2.8801 ± 0.2695 |
| Fixed nonadaptive 20-item paper + NCD | 0.7119 ± 0.0049 | 0.6667 ± 0.0047 | 0.6583 ± 0.0312 | 1.7762 ± 0.3203 |
| PCAT TOEIC adaptation + NCD | 0.7194 ± 0.0083 | 0.6731 ± 0.0052 | 0.6880 ± 0.0228 | 1.7275 ± 0.2609 |
| PCAT with extra shrinkage (separate ablation) | 0.7291 ± 0.0111 | 0.6807 ± 0.0081 | 0.6880 ± 0.0228 | 1.7275 ± 0.2609 |

The primary PCAT method exceeds random on AUC and ACC in all five test splits. Its mean AUC and ACC also exceed the fixed-paper baseline, although seed 24 has lower ACC than fixed; five repeats alone do not establish statistical significance. The shrinkage row is a project-specific ablation, not the paper's primary PCAT method. Full per-seed results and selected papers are in `scripts/run_code/Dense_EdNetTOEIC_Balanced90_90d_paper_query_100gen_80pop_seeds20-21-22-23-24_benchmark_evaluation_results.json`.

The smaller search below remains a quick pipeline check:

```powershell
..\..\.venv\Scripts\python.exe main.py --generations 4 --population 12 --offspring 6 --seeds 20,21,22,23,24 --device cpu
```

This updated-method five-seed run completed on 242 training and 61 test learners per split. Each student answered 20 questions and was evaluated on their other 70:

| Method | Query AUC mean | AUC std | Query ACC mean |
| --- | ---: | ---: | ---: |
| Random 20-item selection + NCD | 0.7020 | 0.0098 | 0.6570 |
| Fixed nonadaptive 20-item paper + NCD | 0.6963 | 0.0116 | 0.6559 |
| PCAT TOEIC adaptation + NCD | 0.7068 | 0.0150 | 0.6609 |
| PCAT with extra shrinkage (separate ablation) | 0.7190 | 0.0152 | 0.6719 |

See `scripts/run_code/Dense_EdNetTOEIC_Balanced90_90d_paper_query_4gen_12pop_5seeds_benchmark_evaluation_results.json` for all five splits and selected papers. All splits routed 31 test learners to hard and 30 to easy. These numbers are a pipeline check under a small search, not evidence for the paper-sized 100-generation, 80-population setting or a robust advantage over random. The selected 30-item papers contain 22–24 distinct Q-matrix attribute combinations. An exact bundle-selection optimization shows that even without the three 10-item stage-capacity constraints, the 90-item bank permits at most 27 distinct combinations in a 30-item bundle-complete paper. Thus strict one-type-per-question uniqueness cannot coexist with indivisible TOEIC bundles in this bank; the remaining difference from the paper is structural.

The following **previous** full-bank query-protocol run completed on five 80/20 learner splits (242 train, 61 test each). It used the older synthetic question-type IDs, lacked guaranteed easy/medium/hard ordering, and used different NCD adaptation settings for search and test. Its AUC/ACC values on each learner's 70 unadministered questions are retained only as historical results:

| Method | Query AUC mean | AUC std | Query ACC mean |
| --- | ---: | ---: | ---: |
| Random 20-item selection + NCD | 0.7029 | 0.0079 | 0.6593 |
| Fixed nonadaptive 20-item paper + NCD | 0.7100 | 0.0075 | 0.6654 |
| PCAT with mastery ranking + NCD | 0.7140 | 0.0030 | 0.6679 |
| PCAT with additional shrinkage (project ablation) | 0.7245 | 0.0068 | 0.6785 |

The result is in `scripts/run_code/Dense_EdNetTOEIC_Balanced90_90d_paper_query_12gen_20pop_5seeds_benchmark_evaluation_results.json`. The added shrinkage is a separate project ablation, not part of the paper's primary method. Query item IDs can differ between methods because their administered papers differ. These numbers should not be used to describe the updated algorithm or the paper-sized default of 100 generations and population 80.

The following **previous** reduced-search five-seed run (242 training and 61 test learners per split) reserved 20 common evaluation questions and optimized papers over only the other 70. It is retained for comparison, but its numbers must not be described as the current paper-style evaluation:

| Method | AUC mean | AUC std | ACC mean |
| --- | ---: | ---: | ---: |
| Random 20-item selection + NCD | 0.6750 | 0.0192 | 0.6516 |
| Fixed nonadaptive 20-item paper + NCD | 0.6647 | 0.0193 | 0.6356 |
| PCAT with paper-described mastery ranking + NCD | 0.6736 | 0.0180 | 0.6462 |
| PCAT with additional shrinkage (project ablation) | 0.6782 | 0.0216 | 0.6508 |

See `scripts/run_code/Dense_EdNetTOEIC_Balanced90_90d_paper_mastery_12gen_20pop_5seeds_benchmark_evaluation_results.json` for that earlier run's per-seed values. Its adaptive method did **not** outperform the random baseline on the fixed 20-item AUC. These numbers do not evaluate the current full-bank query protocol or the default 100-generation, 80-population search.

The **previous** three-seed run (seeds 20, 21, 22; 212 train, 45 validation, 46 test learners per split) used a different raw-score routing rule and a three-objective search. Its numbers below are retained only as historical results and must not be presented as the PDF-aligned method:

| Method | AUC mean | AUC std | ACC mean |
| --- | ---: | ---: | ---: |
| Random 20-item selection + NCD | 0.6991 | 0.0025 | 0.6630 |
| Fixed nonadaptive 20-item paper + NCD | 0.7061 | 0.0044 | 0.6714 |
| PCAT adaptive + NCD | 0.7080 | 0.0024 | 0.6707 |

Those older per-seed metrics and selected papers are saved in `scripts/run_code/Dense_EdNetTOEIC_Balanced90_90d_benchmark_evaluation_results.json`. The PCAT–fixed AUC difference was only 0.0019 across three splits; this did not establish a reliable improvement. New result files contain `paper_mastery` in their names and must be interpreted separately. The 24 Q-matrix concepts in the balanced bank are seven official Part indicators and 17 selected EdNet tag indicators; tag IDs are not interpreted as named grammar skills.
