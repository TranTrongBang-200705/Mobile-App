"""Find complete-case EdNet KT1 cohorts for a multi-part PCAT benchmark.

Question selection uses only response *presence* and official item metadata.
Correctness is deliberately excluded so benchmark accuracy cannot be selected
after seeing labels. Every multi-item bundle is kept intact.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.sparse import csr_matrix


ROOT = Path(__file__).resolve().parents[2]
SETS_PATH = ROOT / "scratch" / "ednet_reselection" / "user_question_sets.parquet"
QUESTIONS_CSV = ROOT / "scratch" / "ednet_sample" / "questions.csv"
OUTPUT_PATH = ROOT / "scratch" / "ednet_reselection" / "cohort_candidates_balanced.json"

# A small yet usable Part floor for a 20-item two-stage PCAT experiment. The
# final bank needs at least 30 selectable and 20 common-evaluation questions.
MIN_ITEMS_BY_PART = {1: 2, 2: 6, 3: 6, 4: 6, 5: 12, 6: 8, 7: 8}
PREFERRED_ITEMS_BY_PART = {1: 3, 2: 9, 3: 9, 4: 9, 5: 18, 6: 10, 7: 12}
MAX_ITEMS_BY_PART = {1: 5, 2: 12, 3: 15, 4: 15, 5: 25, 6: 12, 7: 18}
PART_ORDER = (7, 6, 3, 4, 2, 1, 5)


def load_index():
    print("Loading per-student question sets", flush=True)
    table = pq.read_table(SETS_PATH, columns=["subject_id", "items", "n_unique", "old_bank_overlap"])
    item_col = table["items"].combine_chunks()
    offsets = item_col.offsets.to_numpy(zero_copy_only=False).astype(np.int32, copy=False)
    qids = item_col.values.to_numpy(zero_copy_only=False).astype(np.int32, copy=False)
    n_users = len(table)
    max_qid = int(qids.max())
    matrix = csr_matrix((np.ones(len(qids), dtype=np.uint8), qids, offsets), shape=(n_users, max_qid + 1))
    csc = matrix.tocsc()
    n_unique = table["n_unique"].to_numpy().astype(np.int32, copy=False)
    old_overlap = table["old_bank_overlap"].to_numpy().astype(np.int32, copy=False)
    subjects = table["subject_id"].to_pylist()
    print(f"Indexed {n_users:,} users, {len(qids):,} unique user-question pairs, {max_qid + 1:,} question IDs", flush=True)
    return csc, n_unique, old_overlap, subjects


def bundle_index(csc, metadata):
    groups = metadata.groupby("bundle_id", sort=False)
    bundles = {}
    supporters = {}
    by_part = defaultdict(list)
    for bundle_id, frame in groups:
        qids = tuple(sorted(frame["qnum"].astype(int)))
        parts = set(frame["part"].astype(int))
        if len(parts) != 1:
            continue
        part = next(iter(parts))
        if max(qids) >= csc.shape[1]:
            continue
        counts = [int(csc.indptr[q + 1] - csc.indptr[q]) for q in qids]
        if min(counts) < 50:
            continue
        order = sorted(qids, key=lambda q: csc.indptr[q + 1] - csc.indptr[q])
        users = csc.indices[csc.indptr[order[0]]:csc.indptr[order[0] + 1]]
        for q in order[1:]:
            users = np.intersect1d(users, csc.indices[csc.indptr[q]:csc.indptr[q + 1]], assume_unique=True)
            if len(users) < 50:
                break
        if len(users) < 50:
            continue
        bundles[str(bundle_id)] = {"part": part, "qids": qids}
        supporters[str(bundle_id)] = users
        by_part[part].append(str(bundle_id))
    for part in by_part:
        by_part[part].sort(key=lambda b: (-len(supporters[b]), -len(bundles[b]["qids"]), b))
    print("Eligible complete bundles by Part:", {p: len(by_part[p]) for p in range(1, 8)}, flush=True)
    print("Top bundle supports:", {p: len(supporters[by_part[p][0]]) if by_part[p] else 0 for p in range(1, 8)}, flush=True)
    return bundles, supporters, by_part


def greedy_cohort(seed, min_users, target_questions, candidate_bundles, bundles, supporters):
    selected = [seed]
    selected_set = {seed}
    users = supporters[seed]
    counts = Counter({bundles[seed]["part"]: len(bundles[seed]["qids"])})
    n_questions = len(bundles[seed]["qids"])
    if len(users) < min_users:
        return None

    for part in PART_ORDER:
        while counts[part] < MIN_ITEMS_BY_PART[part]:
            choices = []
            for bundle_id in candidate_bundles[part]:
                if bundle_id in selected_set:
                    continue
                bundle_len = len(bundles[bundle_id]["qids"])
                if n_questions + bundle_len > target_questions:
                    continue
                if counts[part] + bundle_len > MAX_ITEMS_BY_PART[part]:
                    continue
                common = np.intersect1d(users, supporters[bundle_id], assume_unique=True)
                if len(common) >= min_users:
                    choices.append((len(common), bundle_len, bundle_id, common))
            if not choices:
                return None
            _, bundle_len, chosen, users = max(choices, key=lambda item: (item[0], item[1], item[2]))
            selected.append(chosen)
            selected_set.add(chosen)
            counts[part] += bundle_len
            n_questions += bundle_len

    all_candidates = [b for part in range(1, 8) for b in candidate_bundles[part]]
    while n_questions < target_questions:
        choices = []
        for bundle_id in all_candidates:
            if bundle_id in selected_set:
                continue
            part = bundles[bundle_id]["part"]
            bundle_len = len(bundles[bundle_id]["qids"])
            if n_questions + bundle_len > target_questions:
                continue
            if counts[part] + bundle_len > MAX_ITEMS_BY_PART[part]:
                continue
            common = np.intersect1d(users, supporters[bundle_id], assume_unique=True)
            if len(common) < min_users:
                continue
            part_deficit = max(0, PREFERRED_ITEMS_BY_PART[part] - counts[part]) / PREFERRED_ITEMS_BY_PART[part]
            retention = len(common) / len(users)
            score = retention + 0.025 * part_deficit + 0.001 * bundle_len
            choices.append((score, len(common), bundle_len, bundle_id, common))
        if not choices:
            break
        _, _, bundle_len, chosen, users = max(choices, key=lambda item: item[:4])
        selected.append(chosen)
        selected_set.add(chosen)
        counts[bundles[chosen]["part"]] += bundle_len
        n_questions += bundle_len

    if n_questions < 50:
        return None
    qids = sorted(q for b in selected for q in bundles[b]["qids"])
    assert len(qids) == len(set(qids)) == n_questions
    assert all(counts[part] >= MIN_ITEMS_BY_PART[part] for part in range(1, 8))
    return {
        "seed_bundle": seed,
        "target_min_users": min_users,
        "target_questions": target_questions,
        "num_students": len(users),
        "num_questions": n_questions,
        "num_interactions": len(users) * n_questions,
        "part_distribution": {str(p): counts[p] for p in range(1, 8)},
        "bundle_ids": selected,
        "question_numbers": qids,
        "student_row_indices": users.tolist(),
    }


def optimize(seed_count: int, candidates_per_part: int) -> None:
    metadata = pd.read_csv(QUESTIONS_CSV, usecols=["question_id", "bundle_id", "part"])
    metadata["qnum"] = metadata["question_id"].str[1:].astype(int)
    csc, n_unique, old_overlap, subjects = load_index()
    bundles, supporters, by_part = bundle_index(csc, metadata)
    candidates = {p: by_part[p][:candidates_per_part] for p in range(1, 8)}
    seeds = list(dict.fromkeys(by_part[7][:seed_count] + by_part[6][:seed_count]))
    results = []
    for min_users in (80, 100, 150, 200, 300, 500):
        for target_questions in (70, 90):
            for seed in seeds:
                result = greedy_cohort(seed, min_users, target_questions, candidates, bundles, supporters)
                if result is not None:
                    results.append(result)
        print(f"Finished target user floor {min_users}: {len(results)} valid candidates", flush=True)

    # Rank by dataset size and part coverage; this score never uses responses.
    results.sort(
        key=lambda item: (
            item["num_interactions"] * (1 - 0.3 * item["part_distribution"]["5"] / item["num_questions"]),
            item["num_students"], item["num_questions"],
        ),
        reverse=True,
    )
    seen = set()
    unique = []
    for item in results:
        key = tuple(item["question_numbers"])
        if key not in seen:
            seen.add(key)
            item["student_subject_ids"] = [subjects[row] for row in item.pop("student_row_indices")]
            unique.append(item)
        if len(unique) >= 50:
            break
    old_full = int((old_overlap == 94).sum())
    summary = {
        "selection_uses_labels": False,
        "source_user_question_sets": str(SETS_PATH.relative_to(ROOT)),
        "old_94_question_full_students": old_full,
        "minimum_items_per_part": MIN_ITEMS_BY_PART,
        "candidate_search_note": "Greedy multi-start search, not a proof of global optimum; exact complete-case and bundle constraints are verified.",
        "best_candidates": unique,
    }
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Old 94-question bank complete students:", old_full, flush=True)
    print("Saved", len(unique), "candidates to", OUTPUT_PATH, flush=True)
    for item in unique[:10]:
        print(item["num_students"], "students x", item["num_questions"], "questions", item["part_distribution"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-count", type=int, default=6)
    parser.add_argument("--candidates-per-part", type=int, default=30)
    args = parser.parse_args()
    optimize(args.seed_count, args.candidates_per_part)
