"""Make a shorter-time-window sensitivity cohort from the balanced EdNet bank."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from export_ednet_cohorts import ROOT, PCAT_DATA, QUESTION_CSV, SCAN_MANIFEST, export_cohort


def derive(max_days: int) -> None:
    base = PCAT_DATA / "Dense_EdNetTOEIC_Balanced90"
    raw = pd.read_csv(base / "raw_kt1_subset.csv")
    grouped = raw.groupby("subject_id")["timestamp"]
    spans = (grouped.max() - grouped.min()) / 86_400_000
    eligible = set(spans[spans <= max_days].index)
    if len(eligible) < 100:
        raise ValueError(f"Only {len(eligible)} complete students within {max_days} days; too small for this benchmark")
    qnums = sorted(raw["question_id"].str[1:].astype(int).unique().tolist())
    attempts = {
        (str(row.subject_id), int(str(row.question_id)[1:])):
        (int(row.timestamp), int(row.solving_id), str(row.user_answer), int(row.elapsed_time),
         str(row.correct_answer), bool(row.is_correct))
        for row in raw[raw["subject_id"].isin(eligible)].itertuples(index=False)
    }
    source_manifest = json.loads(SCAN_MANIFEST.read_text(encoding="utf-8"))
    metadata = pd.read_csv(QUESTION_CSV)
    metadata["qnum"] = metadata["question_id"].str[1:].astype(int)
    exposure = pd.read_csv(base / "question_exposure.csv")
    global_support = np.zeros(int(metadata["qnum"].max()) + 1, dtype=np.int64)
    global_support[exposure["question_id"].str[1:].astype(int)] = exposure["ednet_users_who_answered"].astype(int)
    name = f"EdNetTOEIC_Balanced90_{max_days}d"
    export_cohort(name, eligible, qnums, attempts, metadata, global_support,
                  source_manifest["users_scanned"], source_manifest, old_bank=False)
    folder = PCAT_DATA / f"Dense_{name}"
    shutil.copyfile(base / "heldout_eval_questions.json", folder / "heldout_eval_questions.json")
    report_path = folder / "data_verification_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["parent_dataset"] = "Dense_EdNetTOEIC_Balanced90"
    report["selection_max_answer_span_days"] = max_days
    report["parent_student_count"] = raw["subject_id"].nunique()
    report["selection_uses_response_labels"] = False
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Retained {len(eligible)} of {raw['subject_id'].nunique()} students whose 90 first answers span <= {max_days} days")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-days", type=int, default=90)
    args = parser.parse_args()
    derive(args.max_days)
