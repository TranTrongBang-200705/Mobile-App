"""Independently check new EdNet data and PCAT bundle/stage invariants."""

from __future__ import annotations

import ast
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "pcat" / "data"
QUESTION_METADATA = pd.read_csv(ROOT / "scratch" / "ednet_sample" / "questions.csv")
QUESTION_METADATA["qnum"] = QUESTION_METADATA["question_id"].str[1:].astype(int)
NAMES = ["Dense_EdNetTOEIC_Full94", "Dense_EdNetTOEIC_Balanced90", "Dense_EdNetTOEIC_Balanced90_90d"]


def load_pcat_helpers():
    path = ROOT / "pcat" / "scripts" / "dense_paper.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    wanted = {"adjust_to_int", "partition_toeic_stages", "decode_unique_questions"}
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    namespace = {"np": np, "defaultdict": defaultdict}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def validate(name: str, helpers: dict) -> dict:
    folder = DATA / name
    report = json.loads((folder / "data_verification_report.json").read_text(encoding="utf-8"))
    raw = pd.read_csv(folder / "raw_kt1_subset.csv")
    total = pd.read_csv(folder / "TotalData.csv", header=None, names=["stu_idx", "q_idx", "correct"])
    catalog = pd.read_csv(folder / "toeic_question_catalog.csv")
    q_matrix = pd.read_csv(folder / "q.csv", header=None).to_numpy(dtype=int)
    exposure = pd.read_csv(folder / "question_exposure.csv")
    heldout = json.loads((folder / "heldout_eval_questions.json").read_text(encoding="utf-8"))["question_indices"]
    n_students, n_questions = report["num_students"], report["num_questions"]
    assert len(raw) == len(total) == n_students * n_questions
    assert raw["subject_id"].nunique() == raw["stu_idx"].nunique() == n_students
    assert raw["question_id"].nunique() == raw["q_idx"].nunique() == n_questions
    assert raw[["stu_idx", "q_idx"]].drop_duplicates().shape[0] == len(raw)
    assert set(raw["stu_idx"]) == set(range(n_students))
    assert set(raw["q_idx"]) == set(range(n_questions))
    assert (raw["is_correct"].astype(int).to_numpy() == total["correct"].to_numpy()).all()
    assert (raw[["stu_idx", "q_idx"]].to_numpy() == total[["stu_idx", "q_idx"]].to_numpy()).all()
    assert (raw["is_correct"] == (raw["user_answer"] == raw["correct_answer"])).all()
    assert q_matrix.shape == (n_questions, report["num_concepts"])
    assert np.all(q_matrix.sum(axis=0) >= 3) and np.all(q_matrix.sum(axis=1) >= 1)
    assert len({tuple(q_matrix[:, i]) for i in range(q_matrix.shape[1])}) == q_matrix.shape[1]
    assert len(heldout) == len(set(heldout)) == 20
    assert set(heldout).issubset(range(n_questions))
    assert set(exposure["q_idx"]) == set(range(n_questions))
    assert np.all((exposure["exposure_rate"] >= 0) & (exposure["exposure_rate"] <= 1))
    assert np.all(q_matrix[heldout].sum(axis=0) <= q_matrix.sum(axis=0) - 2)

    official = QUESTION_METADATA.set_index("question_id")
    for row in catalog.itertuples(index=False):
        source = official.loc[row.question_id]
        assert row.part == source.part and row.bundle_id == source.bundle_id
        assert row.correct_answer == source.correct_answer
    selected_question_ids = set(catalog["question_id"])
    for bundle_id, group in catalog.groupby("bundle_id"):
        all_official = set(QUESTION_METADATA.loc[QUESTION_METADATA["bundle_id"] == bundle_id, "question_id"])
        assert set(group["question_id"]) == all_official, f"Partial bundle {bundle_id} in {name}"
        in_eval = set(group["q_idx"]) & set(heldout)
        assert not in_eval or in_eval == set(group["q_idx"]), f"Split evaluation bundle {bundle_id}"

    # Current PCAT experiment selects from the entire dense bank.  The saved
    # fixed 20-item set is a historical auxiliary artifact, not an exclusion.
    selectable = list(range(n_questions))
    part_map = dict(zip(catalog["q_idx"].astype(int), catalog["part"].astype(int)))
    bundle_map = dict(zip(catalog["q_idx"].astype(int), catalog["bundle_id"].astype(str)))
    concept_map = {i: np.flatnonzero(q_matrix[i]).tolist() for i in range(n_questions)}
    question_type = defaultdict(list)
    know_hash = {}
    next_type = 0
    for q in selectable:
        key = tuple(concept_map[q])
        if key not in know_hash:
            know_hash[key] = next_type
            next_type += 1
        question_type[know_hash[key]].append(q)
    difficulty = np.asarray([1 - p for p in catalog["empirical_accuracy"]], dtype=float)[:, None] * q_matrix
    rng = np.random.default_rng(407)
    checked_papers = 0
    distinct_type_counts = []
    for _ in range(40):
        chromosome = np.r_[rng.uniform(0, max(question_type) + .999, 30), rng.uniform(0, 1, 30)]
        paper = helpers["decode_unique_questions"](chromosome, 30, question_type, difficulty, part_map, bundle_map)
        stages = helpers["partition_toeic_stages"](paper, difficulty, part_map, bundle_map, selectable)
        flat = [q for stage in stages for q in stage]
        assert len(paper) == len(set(paper)) == len(flat) == len(set(flat)) == 30
        assert paper == flat and set(flat).issubset(selectable), (name, paper, flat)
        assert all(len(stage) == 10 for stage in stages)
        mean_difficulty = [float(np.mean([difficulty[q][q_matrix[q] != 0].mean() for q in stage])) for stage in stages]
        assert mean_difficulty[0] <= mean_difficulty[1] <= mean_difficulty[2]
        distinct_types = len({tuple(q_matrix[q]) for q in flat})
        distinct_type_counts.append(distinct_types)
        if n_questions == 90:
            assert distinct_types >= 20, f"Low attribute diversity in {name}: {distinct_types}"
        for bundle_id, group in catalog.groupby("bundle_id"):
            members = set(group["q_idx"])
            if members & set(flat):
                assert members.issubset(flat), f"Fragmented paper bundle {bundle_id}"
                assert any(members.issubset(stage) for stage in stages), f"Split stage bundle {bundle_id}"
        checked_papers += 1
    return {
        "dataset": name,
        "students": n_students,
        "questions": n_questions,
        "responses": len(raw),
        "query_items_per_learner": n_questions - 20,
        "candidate_items": len(selectable),
        "random_pcat_papers_checked": checked_papers,
        "min_distinct_attribute_types_in_checked_papers": min(distinct_type_counts),
        "complete_and_bundle_safe": True,
    }


if __name__ == "__main__":
    helpers = load_pcat_helpers()
    results = [validate(name, helpers) for name in NAMES]
    print(json.dumps(results, indent=2))
