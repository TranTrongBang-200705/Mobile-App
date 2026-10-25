"""Compare the original and newly extracted EdNet PCAT cohorts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "pcat" / "data"
OUT = ROOT / "scratch" / "ednet_reselection" / "cohort_comparison.json"
NAMES = [
    "Dense_EdNetTOEIC", "Dense_EdNetTOEIC_Full94",
    "Dense_EdNetTOEIC_Balanced90", "Dense_EdNetTOEIC_Balanced90_90d",
]


def describe(name: str):
    raw = pd.read_csv(DATA / name / "raw_kt1_subset.csv")
    catalog = pd.read_csv(DATA / name / "toeic_question_catalog.csv")
    grouped = raw.groupby("subject_id")
    spans = (grouped["timestamp"].max() - grouped["timestamp"].min()) / 86_400_000
    student_accuracy = grouped["is_correct"].mean()
    question_accuracy = raw.groupby("question_id")["is_correct"].mean()
    return {
        "students": raw["subject_id"].nunique(),
        "questions": raw["question_id"].nunique(),
        "responses": len(raw),
        "part_distribution": {str(int(k)): int(v) for k, v in catalog["part"].value_counts().sort_index().items()},
        "positive_rate": round(float(raw["is_correct"].mean()), 4),
        "student_accuracy_std": round(float(student_accuracy.std()), 4),
        "question_accuracy_std": round(float(question_accuracy.std()), 4),
        "time_span_days": {
            "median": round(float(spans.median()), 1),
            "p25": round(float(spans.quantile(.25)), 1),
            "p75": round(float(spans.quantile(.75)), 1),
            "p90": round(float(spans.quantile(.90)), 1),
            **{f"users_within_{days}_days": int((spans <= days).sum()) for days in (1, 7, 30, 90, 180, 365)},
        },
    }, raw


def main():
    report = {}
    frames = {}
    for name in NAMES:
        report[name], frames[name] = describe(name)
    old = frames[NAMES[0]]
    first = frames[NAMES[1]]
    matched = old.merge(first, on=["subject_id", "question_id"], suffixes=("_old", "_first"))
    report["original_vs_first_attempt_for_same_179_students"] = {
        "matched_responses": len(matched),
        "same_timestamp_fraction": round(float((matched["timestamp_old"] == matched["timestamp_first"]).mean()), 4),
        "same_user_answer_fraction": round(float((matched["user_answer_old"] == matched["user_answer_first"]).mean()), 4),
        "same_correctness_fraction": round(float((matched["is_correct_old"] == matched["is_correct_first"]).mean()), 4),
        "new_first_attempt_is_earlier_fraction": round(float((matched["timestamp_first"] < matched["timestamp_old"]).mean()), 4),
    }
    balanced = frames[NAMES[2]]
    report["overlap"] = {
        "balanced_and_full94_students": len(set(balanced["subject_id"]) & set(first["subject_id"])),
        "balanced_and_old94_questions": len(set(balanced["question_id"]) & set(old["question_id"])),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
