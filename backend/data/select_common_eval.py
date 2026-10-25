"""Reserve a fixed, bundle-complete 20-item query set for a dense PCAT bank."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp


def reserve(folder: Path, target: int = 20) -> dict:
    catalog = pd.read_csv(folder / "toeic_question_catalog.csv")
    q_matrix = pd.read_csv(folder / "q.csv", header=None).to_numpy(dtype=int)
    if len(catalog) != q_matrix.shape[0]:
        raise ValueError("Question catalog and Q-matrix row counts differ")
    bundles = []
    for bundle_id, group in catalog.groupby("bundle_id", sort=True):
        parts = set(group["part"].astype(int))
        if len(parts) != 1:
            raise ValueError(f"Bundle {bundle_id} crosses Parts")
        bundles.append((str(bundle_id), int(next(iter(parts))), group["q_idx"].astype(int).tolist()))
    n_b = len(bundles)
    parts = sorted(catalog["part"].astype(int).unique())
    n_var = n_b + 2 * len(parts)
    rows, lows, highs = [], [], []

    exact_size = np.zeros(n_var)
    exact_size[:n_b] = [len(qids) for _, _, qids in bundles]
    rows.append(exact_size)
    lows.append(float(target))
    highs.append(float(target))

    # Each concept retains at least two selectable questions for the test bank.
    concept_support = q_matrix.sum(axis=0)
    for concept in range(q_matrix.shape[1]):
        row = np.zeros(n_var)
        row[:n_b] = [int(q_matrix[qids, concept].sum()) for _, _, qids in bundles]
        rows.append(row)
        lows.append(-np.inf)
        highs.append(float(concept_support[concept] - 2))

    part_counts = Counter(catalog["part"].astype(int))
    min_selectable = {}
    for part in parts:
        n_part = part_counts[part]
        if part == 1:
            min_keep = 2
        elif part == 2:
            min_keep = 4
        elif part == 5:
            min_keep = 10
        else:
            min_keep = max(len(qids) for _, p, qids in bundles if p == part)
        min_selectable[part] = min(min_keep, n_part)
        row = np.zeros(n_var)
        row[:n_b] = [len(qids) if p == part else 0 for _, p, qids in bundles]
        rows.append(row)
        min_eval = 1 if part in (1, 2, 5) else min(len(qids) for _, p, qids in bundles if p == part)
        lows.append(float(min_eval))
        highs.append(float(n_part - min_selectable[part]))

    # Keep the evaluation mix close to the bank's Part distribution.
    for pos, part in enumerate(parts):
        row = np.zeros(n_var)
        row[:n_b] = [len(qids) if p == part else 0 for _, p, qids in bundles]
        row[n_b + 2 * pos] = -1.0
        row[n_b + 2 * pos + 1] = 1.0
        wanted = target * part_counts[part] / len(catalog)
        rows.append(row)
        lows.append(wanted)
        highs.append(wanted)

    objective = np.zeros(n_var)
    objective[:n_b] = np.arange(n_b) * 1e-6
    objective[n_b:] = 1.0
    integrality = np.zeros(n_var, dtype=int)
    integrality[:n_b] = 1
    lower = np.zeros(n_var)
    upper = np.array([1.0] * n_b + [float(target)] * (n_var - n_b))
    result = milp(
        c=objective, integrality=integrality, bounds=Bounds(lower, upper),
        constraints=LinearConstraint(np.vstack(rows), lows, highs),
        options={"time_limit": 60.0},
    )
    if result.x is None or not result.success:
        raise RuntimeError(f"Could not construct exact held-out set: {result.message}")
    chosen = [bundles[i] for i in range(n_b) if result.x[i] > 0.5]
    qids = sorted(q for _, _, items in chosen for q in items)
    if len(qids) != target or len(set(qids)) != target:
        raise AssertionError("Held-out set is not exactly 20 unique questions")
    remaining_support = (q_matrix.sum(axis=0) - q_matrix[qids].sum(axis=0)).astype(int)
    if remaining_support.min() < 2:
        raise AssertionError("A concept lost selectable support")
    chosen_part_counts = Counter(int(catalog.set_index("q_idx").loc[q, "part"]) for q in qids)
    manifest = {
        "method": "scipy MILP; exact size, whole bundles, >=2 selectable questions per concept, proportional Part mix",
        "question_indices": qids,
        "ednet_question_ids": catalog.set_index("q_idx").loc[qids, "question_id"].tolist(),
        "bundle_ids": [b for b, _, _ in chosen],
        "part_distribution": {f"Part_{part}": chosen_part_counts[part] for part in parts},
        "selectable_part_distribution": {f"Part_{part}": part_counts[part] - chosen_part_counts[part] for part in parts},
        "minimum_selectable_concept_support": int(remaining_support.min()),
    }
    path = folder / "heldout_eval_questions.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir", type=Path)
    parser.add_argument("--target", type=int, default=20)
    args = parser.parse_args()
    reserve(args.dataset_dir, args.target)
