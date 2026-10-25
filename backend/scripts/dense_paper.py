#——————————————————————————————————————————————————————————————
# Evolutionary Multi-Objective Paper Construction (PCAT + Atomic TOEIC Bundles)
# Addresses Codex Round-1, Round-2 & Round-3 Audit Items:
# 1. Atomic bundle handling (`bundle_id`): multi-question bundles (Part 3, 4, 6, 7)
#    are placed in descending size order (`len(bundle)` largest first) before any
#    1-item bundles, guaranteeing that selected multi-item bundles (e.g. [87,88,89,90])
#    are NEVER displaced by 1-item bundles even at small stage lengths (e.g. test_length=12).
# 2. Exact consistency between decoded candidate paper and stage-partitioned paper:
#    `set(paper1 + paper2 + paper3) == set(questions)` in 100% of cases.
# 3. Respects `allowed_questions` when a candidate pool is explicitly supplied.
# 4. Dynamic `part_map` and `bundle_map` lookup, strict uniqueness, and `test_length` validation.
#——————————————————————————————————————————————————————————————

import copy
import hashlib
from collections import defaultdict
import numpy as np
import torch
from pcat_routing import rank_medium_paper_mastery
from dataset.adaptest_dataset import AdapTestDataset
from model.NCD import NCDModel
from pymoo.core.crossover import Crossover
from pymoo.core.mutation import Mutation
from pymoo.core.problem import ElementwiseProblem


def validate_test_length(test_length: int, prob_num: int) -> int:
    """Validate 2-stage test_length and return total 3-stage pool size num_selected."""
    if not isinstance(test_length, (int, np.integer)) or test_length <= 0 or test_length % 2 != 0:
        raise ValueError(
            f"Invalid test_length={test_length}: 2-stage adaptive test requires an even "
            f"positive integer so Stage 1 and Stage 2 have equal length (test_length // 2)."
        )
    paper_length = test_length // 2
    num_selected = 3 * paper_length
    if num_selected > prob_num:
        raise ValueError(
            f"Invalid test_length={test_length}: requires num_selected={num_selected} items, "
            f"which exceeds available candidate pool size ({prob_num})."
        )
    return num_selected


def difficulty_bounds(question_difficulty):
    """Bounds of actual item difficulty, excluding zeroed-out Q-matrix cells."""
    values = []
    for row in np.asarray(question_difficulty):
        active = row[row != 0]
        if len(active) == 0:
            raise ValueError("Each item must assess at least one attribute")
        values.append(float(np.mean(active)))
    return min(values), max(values)


def cal_COV_EXP(question_overlap, concept_map, metadata, test_length, selected_probs, test_stu):
    stu_coverages = {}
    stu_overlaps = {}
    for stu in test_stu:
        concepts = set()
        overlap = 0.0
        for prob in selected_probs[stu]:
            overlap += (question_overlap[prob] - test_length / metadata['prob_num']) ** 2
            concepts.update(concept_map[prob])
        stu_coverages[stu] = len(concepts) / metadata['know_num']
        stu_overlaps[stu] = overlap / (test_length / metadata['prob_num'])
    cov = sum(stu_coverages.values()) / max(len(stu_coverages), 1)
    exp = sum(stu_overlaps.values()) / max(len(stu_overlaps), 1)
    return cov, exp


def adjust_to_int(x, question_type, num_selected, part_map=None, rng=None):
    """
    Safely adjust chromosome type indices using dynamic `part_map` (no hardcoded IDs).
    Supports both `num_selected <= len(question_type)` and `num_selected > len(question_type)`.
    """
    valid_types = sorted(list(question_type.keys()))
    if rng is None:
        rng = np.random
    max_type = len(valid_types)
    int_array = np.clip(x[:num_selected].astype(int), 0, max_type - 1)
    x[:num_selected] = int_array

    type_capacity = {t: len(question_type[t]) for t in valid_types}
    type_usage = defaultdict(int)
    duplicate_positions = []

    for i in range(num_selected):
        val = int(x[i])
        limit = 1 if num_selected <= max_type else type_capacity.get(val, 1)
        if val < 0 or val not in question_type or type_usage[val] >= limit:
            duplicate_positions.append(i)
        else:
            type_usage[val] += 1

    if duplicate_positions:
        unused = [t for t in valid_types if type_usage[t] == 0]
        rng.shuffle(unused)
        for i in duplicate_positions:
            if unused:
                chosen = unused.pop()
            else:
                avail_cap = [t for t in valid_types if type_usage[t] < type_capacity[t]]
                if avail_cap:
                    min_u = min(type_usage[t] for t in avail_cap)
                    candidates = [t for t in avail_cap if type_usage[t] == min_u]
                    chosen = int(rng.choice(candidates))
                else:
                    chosen = int(rng.choice(valid_types))
            x[i] = chosen
            type_usage[chosen] += 1

    if part_map is not None:
        listening_types = [
            t for t, qs in question_type.items()
            if any(part_map.get(q, 5) in (1, 2, 3, 4) for q in qs)
        ]
        passage_types = [
            t for t, qs in question_type.items()
            if any(part_map.get(q, 5) in (6, 7) for q in qs)
        ]
        current_set = set(int(v) for v in x[:num_selected])

        min_listen = min(3, len(listening_types))
        cur_listen = [t for t in current_set if t in listening_types]
        if len(cur_listen) < min_listen:
            missing_l = [t for t in listening_types if t not in current_set]
            replaceable_pos = [
                idx for idx in range(num_selected)
                if int(x[idx]) not in listening_types and int(x[idx]) not in passage_types
            ]
            for target_t in missing_l[:min_listen - len(cur_listen)]:
                if replaceable_pos:
                    pos = replaceable_pos.pop()
                    x[pos] = target_t
                    current_set.add(target_t)

        min_passage = min(1, len(passage_types))
        cur_passage = [t for t in current_set if t in passage_types]
        if len(cur_passage) < min_passage:
            missing_p = [t for t in passage_types if t not in current_set]
            replaceable_pos = [
                idx for idx in range(num_selected)
                if int(x[idx]) not in listening_types and int(x[idx]) not in passage_types
            ]
            for target_t in missing_p[:min_passage - len(cur_passage)]:
                if replaceable_pos:
                    pos = replaceable_pos.pop()
                    x[pos] = target_t
                    current_set.add(target_t)


def _partition_balanced_toeic_stages(questions, raw_diff, part_map, bundle_map, allowed_pool):
    """Make three bundle-complete papers, each with equal Listening and Reading."""
    paper_length = len(questions) // 3
    if paper_length % 2:
        raise ValueError('Equal Listening/Reading stages require an even stage length.')
    quota = paper_length // 2
    allowed_set = set(allowed_pool)
    if any(int(q) not in allowed_set for q in questions):
        raise ValueError('Candidate paper contains a question outside allowed_questions.')
    if any(q not in part_map or q not in bundle_map for q in allowed_pool):
        raise ValueError('Listening/Reading balance requires complete TOEIC part and bundle metadata.')

    bank_bundles = defaultdict(list)
    for q in allowed_pool:
        bank_bundles[bundle_map[q]].append(q)
    full_bundle_sizes = defaultdict(int)
    for bundle in bundle_map.values():
        full_bundle_sizes[bundle] += 1
    for items in bank_bundles.values():
        items.sort()
        if len(items) != full_bundle_sizes[bundle_map[items[0]]]:
            raise ValueError('allowed_questions contains an incomplete TOEIC bundle.')

    def modality(items):
        modes = {'listening' if part_map[q] in (1, 2, 3, 4) else
                 'reading' if part_map[q] in (5, 6, 7) else 'invalid' for q in items}
        if len(modes) != 1 or 'invalid' in modes:
            raise ValueError(f'TOEIC bundle has mixed or invalid parts: {items}')
        return next(iter(modes))

    for items in bank_bundles.values():
        modality(items)

    # Decoded papers pass through this function again during fitness and test
    # evaluation. Preserve every selected question and bundle on that pass.
    chunks = [list(map(int, questions[s * paper_length:(s + 1) * paper_length])) for s in range(3)]
    if len(set(q for stage in chunks for q in stage)) == len(questions):
        valid = True
        for stage in chunks:
            counts = {'listening': 0, 'reading': 0}
            for q in stage:
                counts[modality([q])] += 1
                if not set(bank_bundles[bundle_map[q]]).issubset(stage):
                    valid = False
            valid &= counts == {'listening': quota, 'reading': quota}
        if valid:
            chunks.sort(key=lambda stage: (np.mean([raw_diff[q] for q in stage]), tuple(sorted(stage))))
            return tuple(chunks)

    selected = set(map(int, questions))
    stages = [[], [], []]
    for mode in ('listening', 'reading'):
        candidates = [
            items for items in bank_bundles.values()
            if modality(items) == mode and any(q in selected for q in items)
        ]
        multi = sorted(
            (items for items in candidates if len(items) > 1 and len(items) <= quota),
            key=lambda items: (-sum(q in selected for q in items), -len(items),
                               np.mean([raw_diff[q] for q in items]), items[0]),
        )
        counts = [0, 0, 0]
        used = set()
        for items in multi:
            possible = [s for s in range(3) if counts[s] + len(items) <= quota]
            if not possible:
                continue
            # Spread bundles across stages. Sorting by measured stage difficulty
            # below still determines which paper is easy, medium, or hard.
            stage = min(possible, key=lambda s: (counts[s], s))
            stages[stage].extend(items)
            counts[stage] += len(items)
            used.update(items)

        preferred_singles = [items[0] for items in candidates if len(items) == 1 and items[0] not in used]
        fallback_singles = [
            items[0] for items in bank_bundles.values()
            if len(items) == 1 and modality(items) == mode
            and items[0] not in used and items[0] not in preferred_singles
        ]
        # Prefer chromosome-selected items, then top up with bank singles.
        # Assign low, middle, and high difficulty questions to different stages.
        for pool in (preferred_singles, fallback_singles):
            pool.sort(key=lambda q: (raw_diff[q], q))
            while pool and any(count < quota for count in counts):
                open_stages = [s for s in range(3) if counts[s] < quota]
                stage = min(open_stages, key=lambda s: (counts[s], s))
                target_rank = (stage + 0.5) / 3
                idx = min(range(len(pool)), key=lambda i: (abs((i + 0.5) / len(pool) - target_rank), i))
                q = pool.pop(idx)
                stages[stage].append(q)
                counts[stage] += 1
        if counts != [quota] * 3:
            raise ValueError(f'Insufficient bundle-safe {mode} items for three {paper_length}-item stages.')

    stages.sort(key=lambda stage: (np.mean([raw_diff[q] for q in stage]), tuple(sorted(stage))))
    assert all(len(stage) == paper_length for stage in stages)
    assert len({q for stage in stages for q in stage}) == 3 * paper_length
    return tuple(stages)


def partition_toeic_stages(questions, question_difficulty, part_map=None, bundle_map=None, allowed_questions=None,
                           content_balance=False):
    """
    Partition `3 * paper_length` questions into 3 equal-length stages:
      - paper1 (Stage 2A - Easy, `paper_length` items)
      - paper2 (Stage 1  - Medium, `paper_length` items)
      - paper3 (Stage 2B - Hard, `paper_length` items)
    Key guarantees:
      1. Multi-item bundles (`len > 1`) are placed FIRST in descending order of bundle size
         (`len(bundle)` largest first), so a 4-item Part 7 bundle or 3-item Part 3/4 bundle
         is NEVER blocked or dropped by 1-item bundles even when `paper_length = 6` (`test_length = 12`).
      2. If `questions` is already a valid bundle-complete set that fits into 3 stages of
         size `paper_length`, `set(paper1 + paper2 + paper3) == set(questions)` is 100% preserved.
      3. Only questions in `allowed_questions` (if provided) are used for any fallback top-up.
    """
    if len(questions) == 0 or len(questions) % 3 != 0:
        raise ValueError(f"Number of candidate questions ({len(questions)}) must be a positive multiple of 3.")
    paper_length = len(questions) // 3
    total_needed = 3 * paper_length

    total_q = len(question_difficulty)
    if allowed_questions is None:
        allowed_pool = list(range(total_q))
    else:
        allowed_pool = sorted(list(allowed_questions))

    raw_diff = {}
    for q in range(total_q):
        d_vec = question_difficulty[q]
        nz = d_vec[d_vec != 0]
        raw_diff[q] = float(np.mean(nz)) if len(nz) > 0 else 0.5
    for q in questions:
        if q not in raw_diff:
            raw_diff[q] = 0.5

    if content_balance:
        if part_map is None or bundle_map is None:
            raise ValueError('Listening/Reading balance requires TOEIC part and bundle metadata.')
        return _partition_balanced_toeic_stages(
            questions, raw_diff, part_map, bundle_map, allowed_pool
        )

    if bundle_map is None:
        unique_q = list(dict.fromkeys(int(q) for q in questions))
        if len(unique_q) < total_needed:
            for q in allowed_pool:
                if q not in unique_q:
                    unique_q.append(q)
                if len(unique_q) == total_needed:
                    break
        sorted_q = sorted(unique_q[:total_needed], key=lambda p: raw_diff[p])
        return (
            sorted_q[0:paper_length],
            sorted_q[paper_length:2 * paper_length],
            sorted_q[2 * paper_length:3 * paper_length],
        )

    allowed_set = set(allowed_pool) | set(int(q) for q in questions)
    bank_bundles = defaultdict(list)
    for q_id, b_id in bundle_map.items():
        if int(q_id) in allowed_set:
            bank_bundles[b_id].append(int(q_id))
    for b_id in bank_bundles:
        bank_bundles[b_id].sort()

    input_bundles = []
    seen_b = set()
    for q in questions:
        b_id = bundle_map.get(int(q), f"q_{int(q)}")
        if b_id not in seen_b:
            seen_b.add(b_id)
            full_b = bank_bundles.get(b_id, [int(q)])
            input_bundles.append((b_id, full_b))

    def bundle_diff(b_items):
        return float(np.mean([raw_diff[q] for q in b_items]))

    def is_listening_bundle(b_items):
        if part_map is None:
            return False
        return any(part_map.get(q, 5) in (1, 2, 3, 4) for q in b_items)

    # Separate multi-item bundles (len > 1), 1-item listening bundles, and 1-item reading bundles
    multi_bundles = [b for b in input_bundles if len(b[1]) > 1]
    single_listen_bundles = [b for b in input_bundles if len(b[1]) == 1 and is_listening_bundle(b[1])]
    single_reading_bundles = [b for b in input_bundles if len(b[1]) == 1 and not is_listening_bundle(b[1])]

    stages = [[], [], []]
    used_questions = set()

    # Step 1: Place ALL multi-item bundles FIRST (largest bundle first, e.g. 4-item Part 7 before 3-item Part 3/4)
    # so 1-item bundles can NEVER fragment stage capacity and force dropping a multi-item bundle!
    multi_sorted = sorted(multi_bundles, key=lambda b: (-len(b[1]), bundle_diff(b[1]), str(b[0])))
    for b_id, b_items in multi_sorted:
        b_d = bundle_diff(b_items)
        # Prefer empty stages first so each stage gets at most 1 large bundle when possible
        empty_stages = [s for s in (1, 0, 2) if len(stages[s]) == 0 and len(b_items) <= paper_length]
        if b_d < 0.50:
            tier_order = [0, 1, 2]
        elif b_d < 0.72:
            tier_order = [1, 2, 0]
        else:
            tier_order = [2, 1, 0]
        cand_stages = empty_stages + [s for s in tier_order if s not in empty_stages and len(stages[s]) + len(b_items) <= paper_length]
        for s in cand_stages:
            if len(stages[s]) + len(b_items) <= paper_length and sum(len(stages[k]) for k in range(3)) + len(b_items) <= total_needed:
                stages[s].extend(b_items)
                used_questions.update(b_items)
                break

    # Step 2: Place 1-item Listening bundles into stages that do not yet have Listening (or have room)
    single_listen_sorted = sorted(single_listen_bundles, key=lambda b: (bundle_diff(b[1]), b[1][0]))
    for b_id, b_items in single_listen_sorted:
        if sum(len(stages[k]) for k in range(3)) + 1 > total_needed:
            break
        no_listen_stages = [
            s for s in (0, 1, 2)
            if len(stages[s]) < paper_length and not any(is_listening_bundle([q]) for q in stages[s])
        ]
        avail_stages = no_listen_stages + [s for s in (0, 1, 2) if s not in no_listen_stages and len(stages[s]) < paper_length]
        if avail_stages:
            s_choice = avail_stages[0]
            stages[s_choice].extend(b_items)
            used_questions.update(b_items)

    # Step 3: Fill remaining slots in each stage to exact `paper_length` using 1-item Reading bundles
    single_pool = sorted(
        (b_items[0] for _, b_items in single_reading_bundles if b_items[0] not in used_questions),
        key=lambda q: (raw_diff[q], q)
    )
    slots_needed = sum(paper_length - len(stages[s]) for s in range(3))

    if len(single_pool) < slots_needed:
        for q in allowed_pool:
            b_id = bundle_map.get(q, f"q_{q}")
            if q not in used_questions and q not in single_pool and len(bank_bundles.get(b_id, [q])) == 1:
                single_pool.append(q)
                if len(single_pool) >= slots_needed:
                    break

    single_selected = sorted(single_pool[:slots_needed], key=lambda q: (raw_diff[q], q))
    n0 = paper_length - len(stages[0])
    n1 = paper_length - len(stages[1])
    n2 = paper_length - len(stages[2])

    stages[0].extend(single_selected[:n0])
    stages[1].extend(single_selected[n0:n0 + n1])
    stages[2].extend(single_selected[n0 + n1:n0 + n1 + n2])

    # Capacity and TOEIC bundle constraints determine the initial bins.  Name
    # those bins by their measured NCD difficulty so that stage one is always
    # the medium paper and the two branches are genuinely easier/harder.
    stages.sort(key=lambda items: (float(np.mean([raw_diff[q] for q in items])), tuple(sorted(items))))
    paper1, paper2, paper3 = stages[0], stages[1], stages[2]
    assert len(paper1) == paper_length and len(paper2) == paper_length and len(paper3) == paper_length
    assert len(set(paper1 + paper2 + paper3)) == total_needed
    return paper1, paper2, paper3


def decode_unique_questions(x, num_selected, question_type, question_difficulty, part_map=None, bundle_map=None,
                            content_balance=False):
    """
    Decode chromosome `x` into `num_selected` strictly unique question IDs whose
    bundles are guaranteed to partition cleanly into 3 stages of size `num_selected // 3`
    with ZERO dropped or swapped questions (`set(p1 + p2 + p3) == set(questions)`).
    """
    arr = np.array(x, dtype=float).copy()
    # Fitness evaluation and Pareto export must decode an unchanged chromosome
    # to the same balanced paper. Legacy runs retain their original RNG behavior.
    repair_rng = None
    if content_balance:
        digest = hashlib.blake2b(arr.tobytes(), digest_size=8).digest()
        repair_rng = np.random.default_rng(int.from_bytes(digest, 'little'))
    adjust_to_int(arr[:num_selected], question_type, num_selected,
                  part_map=part_map, rng=repair_rng)

    allowed_questions = sorted({int(q) for qs in question_type.values() for q in qs})
    total_q = len(question_difficulty)
    raw_diff = {
        q: (float(np.mean(question_difficulty[q][question_difficulty[q] != 0]))
            if np.any(question_difficulty[q] != 0) else 0.5)
        for q in range(total_q)
    }

    seed_questions = []
    used = set()
    for i in range(num_selected):
        t_idx = int(arr[i])
        target_d = float(arr[i + num_selected])
        candidates = [j for j in question_type.get(t_idx, []) if j not in used]
        if not candidates:
            candidates = [j for j in allowed_questions if j not in used]
        best_j = min(candidates, key=lambda j: abs(raw_diff[j] - target_d))
        seed_questions.append(int(best_j))
        used.add(int(best_j))

    if bundle_map is None:
        return seed_questions

    if content_balance:
        p1, p2, p3 = partition_toeic_stages(
            seed_questions, question_difficulty, part_map, bundle_map,
            allowed_questions=allowed_questions, content_balance=True
        )
        return p1 + p2 + p3

    bank_bundles = defaultdict(list)
    for q_id in allowed_questions:
        b_id = bundle_map.get(q_id, f"q_{q_id}")
        bank_bundles[b_id].append(int(q_id))
    for b_id in bank_bundles:
        bank_bundles[b_id].sort()

    paper_length = num_selected // 3
    selected_bundles = []
    seen_bundles = set()
    total_count = 0

    # Complete bundles with the least repeated Q-matrix types first.  This
    # preserves more of the chromosome's unique attribute combinations while
    # still treating every TOEIC passage/audio group as an atomic unit.
    def bundle_type_priority(q):
        b_items = bank_bundles[bundle_map.get(q, f"q_{q}")]
        distinct = len({tuple(np.flatnonzero(question_difficulty[item])) for item in b_items})
        return (len(b_items) / distinct, -distinct, int(q))

    ordered_seeds = sorted(seed_questions, key=bundle_type_priority)

    stage_sim = [0, 0, 0]
    for q in ordered_seeds:
        b_id = bundle_map.get(q, f"q_{q}")
        if b_id in seen_bundles:
            continue
        b_items = bank_bundles.get(b_id, [q])
        b_len = len(b_items)
        if total_count + b_len > num_selected:
            continue
        if b_len > 1:
            # Place in the stage with the most remaining room
            best_s = min(range(3), key=lambda s: stage_sim[s])
            if stage_sim[best_s] + b_len <= paper_length:
                stage_sim[best_s] += b_len
            else:
                continue
        seen_bundles.add(b_id)
        selected_bundles.append(b_items)
        total_count += b_len

    if total_count < num_selected:
        chosen_flat = {q for b in selected_bundles for q in b}
        single_unused = [
            q for q in allowed_questions
            if q not in chosen_flat and len(bank_bundles.get(bundle_map.get(q, f"q_{q}"), [q])) == 1
        ]
        for q in single_unused:
            if total_count >= num_selected:
                break
            selected_bundles.append([int(q)])
            total_count += 1

    raw_selected = [q for b in selected_bundles for q in b][:num_selected]
    # Canonicalize through partition_toeic_stages so exported paper and evaluated stages match 100%
    p1, p2, p3 = partition_toeic_stages(
        raw_selected, question_difficulty, part_map, bundle_map, allowed_questions=allowed_questions
    )
    return p1 + p2 + p3


class CustomCrossover(Crossover):
    def __init__(self, num_selected, question_type, a=2, b=2, part_map=None):
        super().__init__(a, b)
        self.num_selected = num_selected
        self.question_type = question_type
        self.part_map = part_map

    def _do(self, problem, X, **kwargs):
        n_parents, n_matings, n_var = X.shape
        Y = np.empty_like(X)

        for i in range(n_matings):
            parent1, parent2 = X[:, i, 0:self.num_selected].copy()
            adjust_to_int(parent1, self.question_type, self.num_selected, part_map=self.part_map)
            adjust_to_int(parent2, self.question_type, self.num_selected, part_map=self.part_map)

            start, end = sorted(np.random.choice(self.num_selected, 2, replace=False))
            offspring1 = np.full(self.num_selected, -1)
            offspring2 = np.full(self.num_selected, -1)

            offspring1[start:end] = parent1[start:end]
            offspring2[start:end] = parent2[start:end]

            offspring1 = self._adjust(offspring1, parent2, end)
            offspring2 = self._adjust(offspring2, parent1, end)

            Y[0, i, 0:self.num_selected] = offspring1
            Y[1, i, 0:self.num_selected] = offspring2

            parent1_d, parent2_d = X[:, i, self.num_selected:]
            start, end = sorted(np.random.choice(self.num_selected, 2, replace=False))
            offspring1_d = parent1_d.copy()
            offspring2_d = parent2_d.copy()

            offspring1_d[start:end] = parent2_d[start:end]
            offspring2_d[start:end] = parent1_d[start:end]

            Y[0, i, self.num_selected:] = offspring1_d
            Y[1, i, self.num_selected:] = offspring2_d

        return Y

    def _adjust(self, offspring, parent, end):
        current_pos = end
        n_var = self.num_selected
        valid_types = sorted(list(self.question_type.keys()))
        for i in range(len(offspring)):
            if offspring[i] == -1:
                steps = 0
                while int(parent[current_pos % n_var]) in offspring and steps < n_var:
                    current_pos += 1
                    steps += 1
                if steps < n_var:
                    offspring[i] = int(parent[current_pos % n_var])
                    current_pos += 1
                else:
                    unused = [t for t in valid_types if t not in offspring]
                    offspring[i] = int(np.random.choice(unused if unused else valid_types))
        return offspring


class CustomMutation(Mutation):
    def __init__(self, num_selected, question_type, maxmin_difficulty, prob_mutation=0.5, part_map=None):
        super().__init__()
        self.num_selected = num_selected
        self.prob_mutation = prob_mutation
        self.question_type = question_type
        self.maxmin_difficulty = maxmin_difficulty
        self.part_map = part_map

    def _do(self, problem, X, **kwargs):
        valid_types = sorted(list(self.question_type.keys()))
        for i in range(X.shape[0]):
            adjust_to_int(X[i][:self.num_selected], self.question_type, self.num_selected, part_map=self.part_map)
            for j in range(self.num_selected):
                if np.random.rand() < self.prob_mutation:
                    x = np.delete(X[i][0:self.num_selected].copy(), j)
                    unused = [t for t in valid_types if float(t) not in x]
                    X[i][j] = int(np.random.choice(unused if unused else valid_types))

                if np.random.rand() < self.prob_mutation:
                    X[i][j + self.num_selected] = X[i][j + self.num_selected] + np.random.normal(loc=0.0, scale=0.5)
            X[i][self.num_selected:] = np.clip(
                X[i][self.num_selected:],
                min(self.maxmin_difficulty), max(self.maxmin_difficulty)
            )
        return X


class Paper(ElementwiseProblem):
    def __init__(self, paper_config):
        num_selected = int(paper_config['num_selected'])
        if num_selected <= 0 or num_selected % 3 != 0:
            raise ValueError(f"num_selected ({num_selected}) must be a positive multiple of 3.")
        if num_selected > paper_config['metadata']['prob_num']:
            raise ValueError(f"num_selected ({num_selected}) exceeds prob_num ({paper_config['metadata']['prob_num']}).")

        self.use_exp = bool(paper_config.get('use_exp', False))
        n_obj = 4 if self.use_exp else 3
        min_difficulty, max_difficulty = difficulty_bounds(paper_config['question_difficulty'])
        super().__init__(
            n_var=num_selected * 2,
            n_obj=n_obj,
            xl=np.array([0] * num_selected + [min_difficulty] * num_selected, dtype=float),
            xu=np.array([max(paper_config['question_type'].keys())] * num_selected + [max_difficulty] * num_selected, dtype=float),
            type_var=float
        )

        self.metadata = paper_config['metadata']
        self.num_selected = num_selected
        self.concept_map = paper_config['concept_map']
        self.question_overlap = paper_config['question_overlap']
        self.model_true = paper_config['model_true']
        self.train_stu = paper_config['train_stu']
        self.ckpt_path = paper_config['ckpt_path']
        self.question_difficulty = paper_config['question_difficulty']
        self.device = paper_config['device']
        self.question_type = paper_config['question_type']
        self.seed = paper_config['seed']
        self.config = copy.deepcopy(paper_config['config'])
        self.train_triplets = paper_config['train_triplets']
        self.part_map = paper_config.get('part_map', None)
        self.bundle_map = paper_config.get('bundle_map', None)
        self.content_balance = bool(paper_config.get('content_balance', False))
        self.allowed_questions = sorted({int(q) for qs in self.question_type.values() for q in qs})

    def calculate_ACC(self, questions):
        paper1, paper2, paper3 = partition_toeic_stages(
            questions, self.question_difficulty, self.part_map, self.bundle_map,
            allowed_questions=self.allowed_questions, content_balance=self.content_balance
        )
        paper_length = len(paper2)
        test_length = 2 * paper_length

        new_train_data = AdapTestDataset(
            self.train_triplets, self.concept_map,
            self.metadata['stu_num'], self.metadata['prob_num'],
            self.metadata['know_num'], self.seed
        )
        new_train_data.reset2()

        local_cfg = copy.deepcopy(self.config)
        # Fitness must simulate the same NCD adaptation used on the test split.
        local_cfg['num_epochs'] = 10
        local_cfg['batch_size'] = 64
        model = NCDModel(**local_cfg)
        model.init_model(new_train_data)
        model.adaptest_load(self.ckpt_path)

        stu_cov = {}
        stu_exp = {}
        partial_concepts = {}
        partial_overlap = {}
        target_rate = test_length / self.metadata['prob_num']
        for stu in self.train_stu:
            concepts = set()
            overlap = 0.0
            for prob in paper2:
                new_train_data.apply_selection(stu, prob)
                overlap += (self.question_overlap[prob] - target_rate) ** 2
                concepts.update(self.concept_map[prob])
            partial_concepts[stu] = concepts
            partial_overlap[stu] = overlap

        hard_students, _ = rank_medium_paper_mastery(
            model, new_train_data, self.train_stu, paper2, self.concept_map
        )
        for stu in self.train_stu:
            concepts = partial_concepts[stu]
            overlap = partial_overlap[stu]
            branch = paper3 if stu in hard_students else paper1
            for prob in branch:
                new_train_data.apply_selection(stu, prob)
                overlap += (self.question_overlap[prob] - target_rate) ** 2
                concepts.update(self.concept_map[prob])
            stu_cov[stu] = len(concepts) / self.metadata['know_num']
            stu_exp[stu] = overlap / max(target_rate, 1e-8)
            new_train_data.meta[stu] = [que for que in range(self.metadata['prob_num']) if que not in new_train_data._tested[stu]]

        cov = sum(stu_cov.values()) / max(len(stu_cov), 1)
        exp = sum(stu_exp.values()) / max(len(stu_exp), 1)

        model.update(new_train_data, out=False)

        outinformation = model.evaluate(new_train_data)
        return outinformation['acc'], outinformation['auc'], cov, exp

    def _evaluate(self, x, out, *args, **kwargs):
        questions = decode_unique_questions(
            x, self.num_selected, self.question_type,
            self.question_difficulty, self.part_map, self.bundle_map,
            content_balance=self.content_balance
        )
        acc, auc, cov, exp = self.calculate_ACC(questions)
        if self.use_exp:
            out["F"] = [-cov, exp, -acc, -auc]
        else:
            out["F"] = [-cov, -acc, -auc]
