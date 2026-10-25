"""Route a cohort between pre-assembled PCAT papers using diagnosed mastery."""

import torch


def rank_medium_paper_mastery(model, adaptest_data, student_ids, medium_questions, concept_map):
    """Return the top half of examinees after diagnosing only stage-one answers.

    The score is the mean NCD mastery over concepts assessed by the medium paper.
    Scores are ranked within the current cohort; student ID breaks exact ties.
    The paper specifies a mastery percentile split but no scalar aggregation or
    tie rule for a multidimensional CDM, so these two choices are explicit here.
    """
    student_ids = sorted(int(s) for s in student_ids)
    if not student_ids:
        raise ValueError("Cannot rank an empty cohort")
    medium_set = set(int(q) for q in medium_questions)
    concepts = sorted({int(c) for q in medium_set for c in concept_map[q]})
    if not concepts:
        raise ValueError("The medium paper does not assess any concepts")
    for sid in student_ids:
        if set(adaptest_data._tested[sid]) != medium_set:
            raise ValueError(f"Student {sid} must have only medium-paper responses before routing")

    # NCD.update resets each examinee to a neutral prior and fits their mastery
    # from the observed medium-paper answers; no stage-two or query labels enter.
    model.update(adaptest_data, out=False)
    with torch.no_grad():
        device = model.model.student_emb.weight.device
        ids = torch.tensor(student_ids, dtype=torch.long, device=device)
        mastery = torch.sigmoid(model.model.student_emb(ids))[:, concepts]
        scores = mastery.mean(dim=1).cpu().tolist()

    score_by_student = dict(zip(student_ids, (float(x) for x in scores)))
    ranked = sorted(student_ids, key=lambda sid: (-score_by_student[sid], sid))
    hard_students = set(ranked[:(len(ranked) + 1) // 2])
    return hard_students, score_by_student
