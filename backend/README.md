# PCAT

***

The implementation for the KDD 2025 paper "Paper-Level Computerized Adaptive Testing for High-Stakes Examination via Multi-Objective Optimization".

The TOEIC adaptation and its independently reselected EdNet KT1 cohorts are documented in [data/EDNET_RESELECTION.md](data/EDNET_RESELECTION.md). The default PCAT run uses `Dense_EdNetTOEIC_Balanced90_90d` (303 learners, 90 questions), mastery-ranked paper routing, and the paper's four objectives. All 90 questions are eligible for paper assembly; after each learner answers 20 questions, their other 70 questions form the query set for AUC/ACC. The previous `Dense_EdNetTOEIC` cohort remains available for comparison. These are offline PCAT benchmarks, separate from the paper's original datasets.

The TOEIC run now balances each 10-question paper separately: the common medium paper, easy branch, and hard branch each contain 5 Listening and 5 Reading questions. Both administered 20-question paths therefore contain 10 Listening and 10 Reading questions, with whole audio/passage bundles kept together. This is a TOEIC-specific constraint added to the PCAT paper-construction method. Balanced runs use `_balancedLR` output/checkpoint names, so the earlier unbalanced benchmark is preserved. Use `--content-balance none` to reproduce that historical run; the historical `run_full_100gen_80pop.py` runner passes this flag explicitly. The balanced mode requires a TOEIC catalog and a test length divisible by four.

The current implementation changes, validation results, and running-job status are recorded in [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md). The separate `scripts/run_code/run_full_balanced_lr.py` runner executes the five 100-generation/80-population balanced seeds one at a time and resumes from optimizer checkpoints. Read `scripts/run_code/full_100gen_80pop_balancedLR_status.json` for progress. `scripts/run_code/audit_live_paper.py` checks whether an optimized paper has question content, audio, and images before it is considered for the app. The historical `pcat_toeic_questions.json` demo is excluded from the live service. The active `pcat_live_questions.json` bank starts empty; see [LIVE_CONTENT.md](LIVE_CONTENT.md) for its requirements. The app stays unavailable until matching live assets exist.

The separate [BOBCAT comparison](data/BOBCAT_BENCHMARK.md) trains an item-level
selection policy on the same five learner splits and scores it with the existing
NCD checkpoints. It includes uniform item-level Random, bundle-integrity metrics,
and resumable policy training without rerunning PCAT's NSGA-II optimization.

***

# 💻 Requirements	

```python
torch==2.3.1+cu118
numpy==1.26.4
pandas==2.2.2
pymoo==0.6.1.5
scikit-learn==1.5.1
```

Please install all the dependencies listed in the `requirements.txt` file by running the following command:

```bash
pip install -r requirements.txt
```

# 🛠️ File distribution

To make it easier for other scholars to use our code, we'll explain the purpose and location of each file in the root directory:  

1.**data** 
Because the dataset is too large, we compress it when we upload it. So before using this code, you should unzip the dataset file using the following command:
```shell
unzip data.zip
```

This folder is used to store the data set after densification of the original data set,as well as the densification handler.  
You can use the following command to process existing data sets or custom data sets.
```shell
python generate_densedata.py
```
After the densification operation, you will obtain dataset like "Dense_X" file.

2.**Data**
This is where the training and testing data object construction code is stored

3.**model**
This folder stores the code for cognitive diagnostic model NCD, related pre-trained models, etc.

4.**strategy**
Various selection algorithm related code is stored.

5.**scripts**
Contains various permission-related code.

# 🛠️ Experiments

Firstly, you need

> cd scripts/run_code

To run our code, run the following:
```shell
python main.py
```

For the full TOEIC-adapted EdNet benchmark (100 NSGA-II generations, population 80, offspring 50, seeds 20–24), run `python run_full_100gen_80pop.py` from `scripts/run_code`. It runs at most two seeds at a time, records progress in `full_100gen_80pop_status.json`, and combines all five results automatically. NCD models and NSGA-II state are saved per seed under `model/ckpt`; restarting the same command resumes the last completed generation of an unfinished seed.

If you want to change the dataset, just replace the parameter of `--dataset` with the name of your target dataset such as "Dense_Assistment17" or "Dense_MOOCRadar" and so on.


If you want to change the test length, just replace the parameter of `--test_length` with the number of your target length such as 20 or 10 and so on.

After running the program, the result file *"Dense_X_output.txt"* will be generated in the run_code directory.

>Noting: In order to provide a more convenient baseline test, our framework is also equipped with other benchmark methods such as random, kil, NCAT, etc. You can change this in the `strategy_list` object in main.py.

# Reference

Mingjia Li, Junkai Tong, Yiyang Huang, Yifei Ding, Hong Qian and Aimin Zhou "Paper-Level Computerized Adaptive Testing for High-Stakes Examination via Multi-Objective Optimization" In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 2025.

## Bibtex
```
@inproceedings{Li2025PCAT,
 author = {Mingjia Li and Junkai Tong and Yiyang Huang and Yifei Ding and Hong Qian and Aimin Zhou},
 booktitle = {Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)},
 title = {Paper-Level Computerized Adaptive Testing for High-Stakes Examination via Multi-Objective Optimization},
 year = {2025},
 pages={1435--1446},
 address = {Toronto, Canada}
}
```
 
