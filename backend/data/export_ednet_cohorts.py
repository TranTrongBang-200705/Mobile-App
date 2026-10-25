"""Export complete-case EdNet cohorts without changing the active dataset.

Two cohorts are produced from the independently scanned KT1 mirror:
* Full94: all users who answered every question in the existing 94-item bank;
* Balanced90: a label-independent, bundle-complete, seven-Part candidate.

For repeated attempts, the earliest recorded answer to each question is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from reselect_ednet_kt1 import ROOT, OUTPUT_DIR, QUESTION_CSV, download_shard


PCAT_DATA = ROOT / "pcat" / "data"
OLD_DIR = PCAT_DATA / "Dense_EdNetTOEIC"
SCAN_MANIFEST = OUTPUT_DIR / "scan_manifest.json"
BALANCED_CANDIDATES = OUTPUT_DIR / "cohort_candidates_balanced.json"
SETS_PATH = OUTPUT_DIR / "user_question_sets.parquet"


def digest_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def parse_tags(value) -> set[int]:
    return {int(item) for item in str(value).split(";") if item.strip().isdigit()}


def build_balanced_concepts(catalog: pd.DataFrame):
    """Use official Part and EdNet tag labels; never infer grammar names."""
    n_q = len(catalog)
    parts = catalog["part"].to_numpy(dtype=int)
    tags_by_row = [parse_tags(value) for value in catalog["tags"]]
    concepts = []
    vectors = []
    for part in range(1, 8):
        vector = (parts == part).astype(int)
        assert vector.sum() > 0
        concepts.append({"name": f"TOEIC_Part_{part}", "domain": f"Part_{part}", "tags": "", "evidence": "Official EdNet questions.csv part column"})
        vectors.append(vector)

    tag_rows = defaultdict(list)
    for idx, tags in enumerate(tags_by_row):
        for tag in tags:
            tag_rows[tag].append(idx)
    tag_candidates = defaultdict(list)
    existing = {tuple(vector.tolist()) for vector in vectors}
    for tag, rows in tag_rows.items():
        if len(rows) < 4 or len(rows) > n_q - 4:
            continue
        vector = np.zeros(n_q, dtype=int)
        vector[rows] = 1
        signature = tuple(vector.tolist())
        if signature in existing:
            continue
        dominant_part, dominant_count = Counter(int(parts[row]) for row in rows).most_common(1)[0]
        tag_candidates[dominant_part].append((dominant_count, len(rows), tag, vector))
    for part in tag_candidates:
        tag_candidates[part].sort(key=lambda item: (-item[0], -item[1], item[2]))

    # Part 1 has only a few items; select tag concepts in the six larger Parts.
    quotas = {1: 0, 2: 3, 3: 3, 4: 2, 5: 4, 6: 2, 7: 3}
    selected_tags = set()
    for part in range(1, 8):
        count = 0
        for _, _, tag, vector in tag_candidates[part]:
            signature = tuple(vector.tolist())
            if tag in selected_tags or signature in existing:
                continue
            concepts.append({"name": f"EdNet_Tag_{tag}", "domain": f"Tag_dominant_Part_{part}", "tags": str(tag), "evidence": "Official EdNet questions.csv expert-annotated tags column"})
            vectors.append(vector)
            existing.add(signature)
            selected_tags.add(tag)
            count += 1
            if count >= quotas[part]:
                break
    if len(concepts) < 24:
        leftovers = sorted(
            (item for items in tag_candidates.values() for item in items),
            key=lambda item: (-item[0], -item[1], item[2]),
        )
        for _, _, tag, vector in leftovers:
            signature = tuple(vector.tolist())
            if tag in selected_tags or signature in existing:
                continue
            concepts.append({"name": f"EdNet_Tag_{tag}", "domain": "EdNet_Tag", "tags": str(tag), "evidence": "Official EdNet questions.csv expert-annotated tags column"})
            vectors.append(vector)
            existing.add(signature)
            selected_tags.add(tag)
            if len(concepts) >= 24:
                break
    q_matrix = np.column_stack(vectors)
    assert q_matrix.shape[0] == n_q
    assert q_matrix.sum(axis=1).min() >= 1
    assert q_matrix.sum(axis=0).min() >= 3
    assert len(existing) == q_matrix.shape[1]

    concept_rows = []
    for idx, (concept, vector) in enumerate(zip(concepts, vectors)):
        q_indices = np.flatnonzero(vector).tolist()
        concept_rows.append({
            "concept_idx": idx,
            "concept_id": f"C{idx:02d}",
            "concept_name": concept["name"],
            "domain": concept["domain"],
            "mapped_ednet_tags": concept["tags"],
            "verified_source_evidence": concept["evidence"],
            "question_count_in_bank": len(q_indices),
            "question_indices": ";".join(map(str, q_indices)),
            "ednet_question_ids": ";".join(catalog.iloc[q_indices]["question_id"]),
        })
    return q_matrix, pd.DataFrame(concept_rows)


def export_cohort(name: str, subjects: set[str], qnums: list[int], attempts: dict, metadata: pd.DataFrame,
                  global_support: np.ndarray, scanned_users: int, source_manifest: dict, old_bank: bool) -> None:
    folder = PCAT_DATA / f"Dense_{name}"
    folder.mkdir(parents=True, exist_ok=True)
    subject_order = sorted(subjects, key=lambda sid: int(sid[1:]))
    q_meta = metadata.set_index("qnum")
    if old_bank:
        old_catalog = pd.read_csv(OLD_DIR / "toeic_question_catalog.csv")
        q_order = old_catalog["question_id"].str[1:].astype(int).tolist()
        assert set(q_order) == set(qnums)
    else:
        q_order = sorted(qnums, key=lambda q: (int(q_meta.loc[q, "part"]), q))
    q_to_idx = {q: idx for idx, q in enumerate(q_order)}
    sid_to_idx = {sid: idx for idx, sid in enumerate(subject_order)}

    rows = []
    for sid in subject_order:
        for qnum in q_order:
            key = (sid, qnum)
            if key not in attempts:
                raise ValueError(f"Missing real KT1 answer for {sid}, q{qnum}")
            timestamp, solving_id, user_answer, elapsed_time, mirror_correct, mirror_label = attempts[key]
            official_correct = str(q_meta.loc[qnum, "correct_answer"])
            label = int(user_answer == official_correct)
            if mirror_correct != official_correct or int(mirror_label) != label:
                raise ValueError(f"EdNet answer mismatch for {sid}, q{qnum}")
            rows.append((timestamp, solving_id, f"q{qnum}", user_answer, elapsed_time,
                         sid, official_correct, bool(label), sid_to_idx[sid], q_to_idx[qnum]))
    raw = pd.DataFrame(rows, columns=[
        "timestamp", "solving_id", "question_id", "user_answer", "elapsed_time",
        "subject_id", "correct_answer", "is_correct", "stu_idx", "q_idx",
    ])
    assert len(raw) == len(subject_order) * len(q_order)
    assert raw[["stu_idx", "q_idx"]].drop_duplicates().shape[0] == len(raw)
    raw_path = folder / "raw_kt1_subset.csv"
    raw.to_csv(raw_path, index=False)
    total = raw[["stu_idx", "q_idx", "is_correct"]].copy()
    total["is_correct"] = total["is_correct"].astype(int)
    total_path = folder / "TotalData.csv"
    total.to_csv(total_path, header=False, index=False)

    catalog = q_meta.loc[q_order, ["question_id", "bundle_id", "explanation_id", "part", "correct_answer", "tags"]].reset_index(drop=True)
    catalog.insert(0, "q_idx", range(len(catalog)))
    if old_bank:
        q_matrix = pd.read_csv(OLD_DIR / "q.csv", header=None).to_numpy(dtype=int)
        concept_catalog = pd.read_csv(OLD_DIR / "concept_catalog.csv")
        assert q_matrix.shape[0] == len(catalog)
    else:
        q_matrix, concept_catalog = build_balanced_concepts(catalog)
    concept_ids = []
    concept_names = []
    for vector in q_matrix:
        ids = np.flatnonzero(vector).tolist()
        concept_ids.append(";".join(f"C{i:02d}" for i in ids))
        concept_names.append(";".join(concept_catalog.iloc[ids]["concept_name"]))
    catalog["concept_ids"] = concept_ids
    catalog["concept_names"] = concept_names
    catalog["observed_responses"] = len(subject_order)
    catalog["imputed_responses"] = 0
    q_accuracy = raw.groupby("q_idx")["is_correct"].mean()
    q_elapsed = raw.groupby("q_idx")["elapsed_time"].mean()
    catalog["empirical_accuracy"] = catalog["q_idx"].map(q_accuracy).round(4)
    catalog["mean_elapsed_time_ms"] = catalog["q_idx"].map(q_elapsed).round(1)
    catalog.to_csv(folder / "toeic_question_catalog.csv", index=False)
    pd.DataFrame(q_matrix).to_csv(folder / "q.csv", header=False, index=False)
    concept_catalog.to_csv(folder / "concept_catalog.csv", index=False, encoding="utf-8-sig")
    (folder / "question_map.json").write_text(json.dumps({str(i): i for i in range(len(q_order))}), encoding="utf-8")
    (folder / "ednet_question_id_map.json").write_text(json.dumps({f"q{q}": q_to_idx[q] for q in q_order}, indent=2), encoding="utf-8")

    student_info = {}
    for sid, frame in raw.groupby("subject_id", sort=False):
        idx = sid_to_idx[sid]
        student_info[str(idx)] = {
            "stu_idx": idx, "ednet_subject_id": sid,
            "observed_count": len(frame), "imputed_count": 0,
            "accuracy": round(float(frame["is_correct"].mean()), 4),
            "min_timestamp": int(frame["timestamp"].min()),
            "max_timestamp": int(frame["timestamp"].max()),
            "mean_elapsed_time_ms": round(float(frame["elapsed_time"].mean()), 1),
        }
    (folder / "student_map.json").write_text(json.dumps(student_info, indent=2), encoding="utf-8")
    exposure = pd.DataFrame({
        "q_idx": range(len(q_order)), "question_id": [f"q{q}" for q in q_order],
        "ednet_users_who_answered": [int(global_support[q]) for q in q_order],
        "ednet_total_users_scanned": scanned_users,
        "exposure_rate": [round(float(global_support[q]) / scanned_users, 8) for q in q_order],
    })
    exposure.to_csv(folder / "question_exposure.csv", index=False)

    report = {
        "dataset": f"Dense_{name}",
        "source": source_manifest["source"],
        "source_scan_manifest": str(SCAN_MANIFEST.relative_to(ROOT)),
        "selection_uses_response_labels": False,
        "attempt_rule": "first recorded attempt by timestamp per student and question",
        "num_students": len(subject_order),
        "num_questions": len(q_order),
        "num_concepts": q_matrix.shape[1],
        "total_interactions": len(raw),
        "imputed_interactions": 0,
        "complete_matrix": True,
        "correctness_verified_against_official_item_answers": True,
        "raw_kt1_subset_sha256": digest_file(raw_path),
        "total_data_sha256": digest_file(total_path),
        "positive_rate": round(float(raw["is_correct"].mean()), 4),
        "part_distribution": {f"Part_{int(part)}": int(count) for part, count in catalog["part"].value_counts().sort_index().items()},
        "min_concept_support": int(q_matrix.sum(axis=0).min()),
        "max_concept_support": int(q_matrix.sum(axis=0).max()),
        "mean_concepts_per_question": round(float(q_matrix.sum(axis=1).mean()), 2),
        "multi_item_bundles": {
            str(bundle): group["q_idx"].astype(int).tolist()
            for bundle, group in catalog.groupby("bundle_id") if len(group) > 1
        },
    }
    (folder / "data_verification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    alias = PCAT_DATA / name
    alias.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(total_path, alias / "TotalData.csv")
    print(f"Exported {name}: {len(subject_order):,} students x {len(q_order)} questions; {len(raw):,} real responses", flush=True)


def main(balanced_index: int) -> None:
    scan_manifest = json.loads(SCAN_MANIFEST.read_text(encoding="utf-8"))
    if len(scan_manifest["shards"]) != 11 or scan_manifest["existing_raw_rows_missing"]:
        raise ValueError("Full EdNet scan and old-subset verification required")
    candidates = json.loads(BALANCED_CANDIDATES.read_text(encoding="utf-8"))["best_candidates"]
    chosen = candidates[balanced_index]
    if chosen["num_questions"] < 70 or set(map(int, chosen["part_distribution"])) != set(range(1, 8)):
        raise ValueError("Balanced candidate must cover all seven Parts with at least 70 questions")
    sets_table = pq.read_table(SETS_PATH, columns=["subject_id", "old_bank_overlap"])
    old_subjects = {
        sid for sid, overlap in zip(sets_table["subject_id"].to_pylist(), sets_table["old_bank_overlap"].to_pylist())
        if overlap == 94
    }
    balanced_subjects = set(chosen["student_subject_ids"])
    old_qids = set(pd.read_csv(OLD_DIR / "toeic_question_catalog.csv")["question_id"].str[1:].astype(int))
    balanced_qids = set(map(int, chosen["question_numbers"]))
    target_subjects = old_subjects | balanced_subjects
    target_qids = {f"q{q}" for q in old_qids | balanced_qids}
    metadata = pd.read_csv(QUESTION_CSV)
    metadata["qnum"] = metadata["question_id"].str[1:].astype(int)
    if len(old_subjects) != scan_manifest["old_bank_complete_users"]:
        raise ValueError("Old-bank cohort count disagrees with scan manifest")
    print(f"Extracting {len(old_subjects):,} old-bank and {len(balanced_subjects):,} balanced-bank students", flush=True)

    best_attempts = {}
    for shard_index, entry in enumerate(scan_manifest["shards"]):
        start = time.time()
        temp_path = Path(tempfile.gettempdir()) / f"ednet_kt1_{shard_index:05d}.parquet"
        digest = download_shard({"path": entry["path"], "size": entry["bytes"]}, temp_path)
        if digest != entry["sha256"]:
            raise ValueError(f"Shard hash mismatch for {entry['path']}")
        parquet = pq.ParquetFile(temp_path)
        for batch in parquet.iter_batches(batch_size=100_000):
            frame = batch.to_pandas()
            relevant = frame[frame["subject_id"].isin(target_subjects) & frame["question_id"].isin(target_qids)]
            for row in relevant.itertuples(index=False):
                sid = str(row.subject_id)
                qnum = int(str(row.question_id)[1:])
                if not ((sid in old_subjects and qnum in old_qids) or (sid in balanced_subjects and qnum in balanced_qids)):
                    continue
                key = (sid, qnum)
                attempt = (int(row.timestamp), int(row.solving_id), str(row.user_answer), int(row.elapsed_time),
                           str(row.correct_answer), bool(row.is_correct))
                if key not in best_attempts or attempt[0] < best_attempts[key][0]:
                    best_attempts[key] = attempt
        del parquet
        temp_path.unlink()
        print(f"Extracted shard {shard_index + 1}/11: {len(best_attempts):,} unique needed answers; {time.time() - start:.1f}s", flush=True)

    # Each user-question presence was checked in the first scan; verify again
    # against actual answer rows before emitting either dataset.
    for name, users, questions in (
        ("EdNetTOEIC_Full94", old_subjects, old_qids),
        ("EdNetTOEIC_Balanced90", balanced_subjects, balanced_qids),
    ):
        missing = [(sid, q) for sid in users for q in questions if (sid, q) not in best_attempts]
        if missing:
            raise ValueError(f"{name} missing {len(missing)} answers; examples: {missing[:5]}")

    item_col = pq.read_table(SETS_PATH, columns=["items"])["items"].combine_chunks()
    all_seen_items = item_col.values.to_numpy(zero_copy_only=False)
    global_support = np.bincount(all_seen_items, minlength=int(metadata["qnum"].max()) + 1)
    export_cohort("EdNetTOEIC_Full94", old_subjects, sorted(old_qids), best_attempts, metadata,
                  global_support, scan_manifest["users_scanned"], scan_manifest, old_bank=True)
    shutil.copyfile(OLD_DIR / "heldout_eval_questions.json",
                    PCAT_DATA / "Dense_EdNetTOEIC_Full94" / "heldout_eval_questions.json")
    export_cohort("EdNetTOEIC_Balanced90", balanced_subjects, sorted(balanced_qids), best_attempts, metadata,
                  global_support, scan_manifest["users_scanned"], scan_manifest, old_bank=False)
    from select_common_eval import reserve
    reserve(PCAT_DATA / "Dense_EdNetTOEIC_Balanced90")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--balanced-index", type=int, default=2)
    args = parser.parse_args()
    main(args.balanced_index)
