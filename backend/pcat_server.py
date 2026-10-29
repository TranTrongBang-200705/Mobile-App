"""
FastAPI Server for PCAT + NCD Adaptive Placement Testing (TOEIC)
Loads the seed-20 optimized paper, with NCD routing/diagnosis and audio.
The paper is unavailable until every selected item has usable live assets.
"""

import os
import sys
import json
import hashlib
import secrets
import threading
import time
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from dataset.adaptest_dataset import AdapTestDataset
from model.NCD import NCDModel

app = FastAPI(
    title="GetGoals PCAT + NCD Adaptive Engine",
    description="TOEIC-inspired PCAT. Live item content must match the EdNet IDs used by the model.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and configs
DATASET_NAME = "Dense_EdNetTOEIC_Balanced90_90d"
DATA_DIR = os.path.join(ROOT_DIR, "data", DATASET_NAME)
CATALOG_PATH = os.path.join(DATA_DIR, "toeic_question_catalog.csv")
Q_PATH = os.path.join(DATA_DIR, "q.csv")
CKPT_PATH = os.path.join(ROOT_DIR, "model", "ckpt", f"model_{DATASET_NAME}_seed20_train_ncd.pt")
QUESTIONS_JSON_PATH = os.path.join(ROOT_DIR, "pcat_live_questions.json")
AUDIO_DIR = os.path.join(ROOT_DIR, "audio_cache")
IMAGE_DIR = os.path.join(ROOT_DIR, "image_cache")
RESULT_7PART_PATH = os.path.join(
    ROOT_DIR, "scripts", "run_code",
    "optimized_7part_paper_seed20.json",
)
RESULT_PATH = os.path.join(
    ROOT_DIR, "scripts", "run_code",
    f"{DATASET_NAME}_paper_query_100gen_80pop_seeds20-21-22-23-24_balancedLR_benchmark_evaluation_results.json",
)
PAPER_SEED = 20  # Matches the NCD checkpoint used by this live service.
PAPER_SOURCE = "optimized_7part_balanced_seed20"


def load_optimized_paper():
    if os.path.exists(RESULT_7PART_PATH):
        with open(RESULT_7PART_PATH, encoding="utf-8") as source:
            data = json.load(source)
        stages = data["stages"]
        if len(data["full_30"]) != 30 or set(data["full_30"]) != {
            q for ids in stages.values() for q in ids
        }:
            raise RuntimeError("Optimized paper's full_30 disagrees with its stages")
        return stages

    with open(RESULT_PATH, encoding="utf-8") as source:
        benchmark = json.load(source)
    method = benchmark.get("methodology", {})
    if (method.get("generations"), method.get("population"), method.get("content_balance")) != (
        100, 80, "5 Listening + 5 Reading in each 10-item stage"
    ):
        raise RuntimeError("The saved benchmark is not the completed balanced-L/R run")
    if PAPER_SEED not in benchmark["seeds_evaluated"]:
        raise RuntimeError(f"Seed {PAPER_SEED} is absent from the optimized benchmark")
    paper = benchmark["per_seed_details"][str(PAPER_SEED)]["selected_paper"]
    stages = {
        "medium": paper["stage1_medium_10"],
        "easy": paper["stage2a_easy_10"],
        "hard": paper["stage2b_hard_10"],
    }
    if len(paper["full_30"]) != 30 or set(paper["full_30"]) != {
        q for ids in stages.values() for q in ids
    }:
        raise RuntimeError("Optimized paper's full_30 disagrees with its stages")
    return stages


OPTIMIZED_STAGES = load_optimized_paper()
STAGE1_MEDIUM_IDS = OPTIMIZED_STAGES["medium"]
STAGE2A_EASY_IDS = OPTIMIZED_STAGES["easy"]
STAGE2B_HARD_IDS = OPTIMIZED_STAGES["hard"]


def find_image_path(q_idx: int):
    for extension in ('.png', '.jpg', '.jpeg'):
        path = os.path.join(IMAGE_DIR, f'{q_idx}{extension}')
        if os.path.isfile(path):
            return path
    return None

SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_LOCK = threading.Lock()
SESSION_TTL_SECONDS = 60 * 60
ROUTING_CALIBRATION_PATH = os.path.join(ROOT_DIR, 'live_routing_calibration.json')


def load_routing_threshold():
    if not os.path.exists(ROUTING_CALIBRATION_PATH):
        return None
    with open(ROUTING_CALIBRATION_PATH, encoding='utf-8') as source:
        calibration = json.load(source)
    digest = hashlib.sha256()
    with open(CKPT_PATH, 'rb') as checkpoint:
        for block in iter(lambda: checkpoint.read(1024 * 1024), b''):
            digest.update(block)
    model_sha256 = digest.hexdigest()
    if (calibration.get('stage1_medium_10') != STAGE1_MEDIUM_IDS or
            calibration.get('model_sha256') != model_sha256):
        return None
    return float(calibration['training_median_mastery'])


ROUTING_THRESHOLD = load_routing_threshold()

with open(QUESTIONS_JSON_PATH, "r", encoding="utf-8") as f:
    QUESTIONS_CONTENT = json.load(f)
if not isinstance(QUESTIONS_CONTENT, dict):
    raise RuntimeError('The live question bank must be a JSON object keyed by q_idx')

catalog_df = pd.read_csv(CATALOG_PATH)
q_df = pd.read_csv(Q_PATH, header=None)
concept_map = {idx: np.where(np.array(row))[0].tolist() for idx, row in enumerate(q_df.values)}
total_questions = len(q_df)
total_concepts = q_df.shape[1]

concept_catalog_path = os.path.join(DATA_DIR, "concept_catalog.csv")
if os.path.exists(concept_catalog_path):
    conc_df = pd.read_csv(concept_catalog_path)
    concept_names = {int(r["concept_idx"]): str(r["concept_name"]) for _, r in conc_df.iterrows()}
else:
    concept_names = {i: f"Kỹ năng {i+1}" for i in range(total_concepts)}


def validate_active_papers():
    stages = OPTIMIZED_STAGES
    selected = [q for stage in stages.values() for q in stage]
    if len(selected) != 30 or len(set(selected)) != 30:
        raise RuntimeError('The three live PCAT stages must have 30 distinct items')
    catalog = catalog_df.set_index('q_idx')
    missing = {'content': [], 'image': [], 'audio': [], 'answer_key': []}
    for name, ids in stages.items():
        if len(ids) != 10:
            raise RuntimeError(f'{name} must contain 10 items')
        if any(q not in catalog.index for q in ids):
            raise RuntimeError(f'{name} contains an unknown catalog item')
        parts = [int(catalog.loc[q, 'part']) for q in ids]
        if sum(part <= 4 for part in parts) != 5:
            raise RuntimeError(f'{name} must contain five Listening and five Reading items')
        for q, part in zip(ids, parts):
            bundle_id = str(catalog.loc[q, 'bundle_id'])
            whole_bundle = set(catalog.index[catalog['bundle_id'].astype(str) == bundle_id])
            if not whole_bundle.issubset(ids):
                raise RuntimeError(f'{name} splits bundle {bundle_id}')
            content = QUESTIONS_CONTENT.get(str(q))
            if (not content or content.get('question_id') != str(catalog.loc[q, 'question_id'])
                    or not content.get('question_text') or not content.get('options')):
                missing['content'].append(q)
            else:
                try:
                    key = int(content['correct_answer_index'])
                    expected = ord(str(catalog.loc[q, 'correct_answer']).lower()) - ord('a')
                    if key < 0 or key >= len(content['options']) or key != expected:
                        missing['answer_key'].append(q)
                except (KeyError, TypeError, ValueError):
                    missing['answer_key'].append(q)
            if part == 1 and find_image_path(q) is None:
                missing['image'].append(q)
            if part <= 4:
                audio_id = str(q) if part <= 2 else bundle_id
                if not os.path.exists(os.path.join(AUDIO_DIR, f'{audio_id}.mp3')):
                    missing['audio'].append(q)
    return {kind: sorted(set(ids)) for kind, ids in missing.items()}


PAPER_ASSET_ISSUES = validate_active_papers()


def require_paper_ready():
    if any(PAPER_ASSET_ISSUES.values()):
        raise HTTPException(
            status_code=503,
            detail='Bộ đề PCAT tối ưu chưa đủ nội dung, ảnh hoặc audio để mở bài thi.',
        )


def get_full_question_data(q_idx: int) -> Dict[str, Any]:
    row = catalog_df[catalog_df["q_idx"] == q_idx].iloc[0]
    str_key = str(q_idx)
    content = QUESTIONS_CONTENT.get(str_key)
    if content is None:
        raise RuntimeError(f"Missing question content for q_idx={q_idx}")
    part = int(row["part"])

    # Xác định file Audio cho phần Listening
    audio_url = None
    if part in (1, 2):
        audio_file = f"{q_idx}.mp3"
        if os.path.exists(os.path.join(AUDIO_DIR, audio_file)):
            audio_url = f"/api/pcat/audio/{q_idx}"
    elif part in (3, 4):
        bundle_file = f"{row['bundle_id']}.mp3"
        if os.path.exists(os.path.join(AUDIO_DIR, bundle_file)):
            audio_url = f"/api/pcat/audio/{row['bundle_id']}"

    return {
        "q_idx": int(q_idx),
        "question_id": str(row["question_id"]),
        "bundle_id": str(row["bundle_id"]),
        "part": part,
        "part_name": content.get("part_name", f"Part {part}"),
        "audio_url": audio_url,
        "image_url": f"/api/pcat/image/{q_idx}" if part == 1 and find_image_path(q_idx) else None,
        "context": content.get("context", ""),
        "question_text": content["question_text"],
        "options": content["options"],
        "correct_answer_index": int(content["correct_answer_index"]),
        "explanation": content.get("explanation", ""),
        "concept_names": str(row["concept_names"]),
    }


def get_public_question_data(q_idx: int) -> Dict[str, Any]:
    question = get_full_question_data(q_idx)
    question.pop('correct_answer_index')
    question.pop('explanation')
    if question['part'] <= 4:
        question['context'] = ''  # Listening transcript is review-only.
    return question


def validate_answers(items, expected_ids):
    actual = [item.q_idx for item in items]
    if len(actual) != len(expected_ids) or set(actual) != set(expected_ids):
        raise HTTPException(status_code=400, detail='Question IDs must match the assigned paper exactly, without duplicates.')
    answers = {item.q_idx: item.selected_answer_index for item in items}
    for q_idx, chosen in answers.items():
        n_options = len(QUESTIONS_CONTENT[str(q_idx)]['options'])
        if chosen < -1 or chosen >= n_options:
            raise HTTPException(status_code=400, detail=f'Invalid answer index for q_idx={q_idx}.')
    return answers


def init_ncd_evaluator(tau: float = 1.0) -> NCDModel:
    cfg = {
        "learning_rate": 0.05,
        "batch_size": 64,
        "num_epochs": 10,
        "num_dim": 1,
        "device": "cpu",
        "cdm": "ncd",
        "prednet_len1": 128,
        "prednet_len2": 64,
        "betas": (0.9, 0.999),
        "policy": "mynew",
        "policy_path": os.path.join(ROOT_DIR, "model", "ckpt", f"{DATASET_NAME}_bocat_policy.pt"),
        "THRESHOLD": 300,
        "start": 0,
        "end": 3000,
        "seed": 20,
        "shrinkage_tau": tau,
    }
    return NCDModel(**cfg)


class AnswerItem(BaseModel):
    q_idx: int
    selected_answer_index: int


class RouteRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = "student_01"
    stage1_answers: List[AnswerItem]


class DiagnoseRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = "student_01"
    all_answers: List[AnswerItem]


@app.get("/")
def health_check():
    return {
        "status": "ready" if not any(PAPER_ASSET_ISSUES.values()) and ROUTING_THRESHOLD is not None else "paper_unavailable",
        "system": "GetGoals PCAT + NCD Adaptive Engine",
        "dataset": DATASET_NAME,
        "test_length": 20,
        "stage1_length": len(STAGE1_MEDIUM_IDS),
        "stage2_length": len(STAGE2A_EASY_IDS),
        "total_active_questions": 30,
        "paper_source": PAPER_SOURCE,
        "paper_seed": PAPER_SEED,
        "asset_issues": PAPER_ASSET_ISSUES,
        "routing_calibrated": ROUTING_THRESHOLD is not None,
        "routing": "training_cohort_median_ncd_proxy",
        "available_endpoints": [
            "GET /api/pcat/stage1",
            "POST /api/pcat/route",
            "POST /api/pcat/diagnose",
            "GET /api/pcat/audio/{item_id}",
            "GET /api/pcat/image/{q_idx}"
        ]
    }


@app.get("/api/pcat/audio/{item_id}")
def get_audio_stream(item_id: str):
    """Phát file audio MP3 cho câu hỏi Listening TOEIC."""
    cache_path = os.path.join(AUDIO_DIR, f"{item_id}.mp3")
    if os.path.exists(cache_path):
        return FileResponse(cache_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail=f"Không tìm thấy file audio cho {item_id}")


@app.get("/api/pcat/image/{q_idx}")
def get_item_image(q_idx: int):
    path = find_image_path(q_idx)
    if path is None:
        raise HTTPException(status_code=404, detail='Không tìm thấy ảnh cho câu hỏi này.')
    return FileResponse(path)


@app.get("/api/pcat/stage1")
def get_stage1_questions():
    """Return the optimized medium paper once all selected assets are ready."""
    require_paper_ready()
    if ROUTING_THRESHOLD is None:
        raise HTTPException(status_code=503, detail='Ngưỡng phân nhánh của bộ đề mới chưa được hiệu chuẩn.')
    questions = [get_public_question_data(q) for q in STAGE1_MEDIUM_IDS]
    session_id = secrets.token_urlsafe(24)
    with SESSION_LOCK:
        now = time.monotonic()
        for old_id in [key for key, value in SESSIONS.items()
                       if now - value['created_at'] > SESSION_TTL_SECONDS]:
            SESSIONS.pop(old_id, None)
        SESSIONS[session_id] = {'created_at': now, 'stage1_answers': None, 'branch': None}
    return {
        "session_id": session_id,
        "question_source": "separate_live_question_bank",
        "paper_source": PAPER_SOURCE,
        "stage": 1,
        "stage_name": "Giai đoạn 1: Đề Cơ sở (Medium - 10 câu)",
        "description": "Bài thi bước đầu đo lường toàn diện các kỹ năng để AI định vị phân vị trình độ",
        "total_questions": len(questions),
        "questions": questions
    }


@app.post("/api/pcat/route")
def route_stage2(request: RouteRequest):
    """Fit NCD to the exact medium paper and choose one fixed Stage 2 branch."""
    require_paper_ready()
    if ROUTING_THRESHOLD is None:
        raise HTTPException(status_code=503, detail='Routing calibration is not available.')
    with SESSION_LOCK:
        session = SESSIONS.get(request.session_id)
        if session is None or time.monotonic() - session['created_at'] > SESSION_TTL_SECONDS:
            session = {
                'created_at': time.monotonic(),
                'branch': None,
                'stage1_answers': None,
            }
            SESSIONS[request.session_id] = session
        elif session['branch'] is not None:
            # Allow re-routing if student resubmits
            session['branch'] = None
    ans_map = validate_answers(request.stage1_answers, STAGE1_MEDIUM_IDS)

    triplets = []
    correct_count = 0

    for q in STAGE1_MEDIUM_IDS:
        q_data = get_full_question_data(q)
        is_corr = 1 if ans_map.get(q, -1) == q_data["correct_answer_index"] else 0
        if is_corr:
            correct_count += 1
        triplets.append((0, q, is_corr))

    adaptest_data = AdapTestDataset(triplets, concept_map, 1, total_questions, total_concepts, 20)
    adaptest_data.reset2()
    for q in STAGE1_MEDIUM_IDS:
        adaptest_data.apply_selection(0, q)

    model = init_ncd_evaluator(tau=0.0)
    model.init_model(adaptest_data)
    model.adaptest_load(CKPT_PATH)
    model.update(adaptest_data, out=False)

    medium_concepts = sorted({c for q in STAGE1_MEDIUM_IDS for c in concept_map[q]})
    with torch.no_grad():
        device = model.model.student_emb.weight.device
        sid = torch.tensor([0], dtype=torch.long, device=device)
        mastery = torch.sigmoid(model.model.student_emb(sid))[:, medium_concepts]
        mastery_score = float(mastery.mean().cpu().item())

    # A live examinee cannot be ranked against a future test cohort. Use the
    # median mastery calibrated on the training cohort for this medium paper.
    is_hard = mastery_score >= ROUTING_THRESHOLD

    chosen_stage2_ids = STAGE2B_HARD_IDS if is_hard else STAGE2A_EASY_IDS
    branch_code = "hard" if is_hard else "easy"
    branch_title = (
        "Chặng 2B: Nhánh Nâng cao (Hard - 10 câu)" if is_hard
        else "Chặng 2A: Nhánh Cơ bản (Easy - 10 câu)"
    )
    branch_desc = (
        "NCD ước lượng năng lực Chặng 1 ở nửa trên của nhóm tham chiếu; chuyển sang đề khó."
        if is_hard else
        "NCD ước lượng năng lực Chặng 1 ở nửa dưới của nhóm tham chiếu; chuyển sang đề dễ."
    )

    with SESSION_LOCK:
        session['stage1_answers'] = ans_map
        session['branch'] = branch_code
    stage2_questions = [get_public_question_data(q) for q in chosen_stage2_ids]

    return {
        "user_id": request.user_id,
        "stage1_correct_count": correct_count,
        "stage1_accuracy_pct": round(correct_count / len(STAGE1_MEDIUM_IDS) * 100, 1),
        "stage1_mastery_score": round(mastery_score, 4),
        "routing_threshold": ROUTING_THRESHOLD,
        "paper_source": PAPER_SOURCE,
        "routed_branch": branch_code,
        "branch_title": branch_title,
        "branch_description": branch_desc,
        "total_stage2_questions": len(stage2_questions),
        "stage2_questions": stage2_questions
    }


@app.post("/api/pcat/diagnose")
def diagnose_full_test(request: DiagnoseRequest):
    """Diagnose only the 20 items actually assigned to this session."""
    require_paper_ready()
    with SESSION_LOCK:
        session = SESSIONS.get(request.session_id)
        if (session is None or session.get('branch') is None or
                time.monotonic() - session.get('created_at', 0) > SESSION_TTL_SECONDS):
            answered_keys = {item.q_idx for item in request.all_answers}
            if set(STAGE2B_HARD_IDS).issubset(answered_keys):
                branch = 'hard'
            elif set(STAGE2A_EASY_IDS).issubset(answered_keys):
                branch = 'easy'
            else:
                branch = 'easy'
            stage1_map = {item.q_idx: item.selected_answer_index for item in request.all_answers if item.q_idx in STAGE1_MEDIUM_IDS}
            session = {
                'created_at': time.monotonic(),
                'branch': branch,
                'stage1_answers': stage1_map,
            }
            SESSIONS[request.session_id] = session
        else:
            branch = session['branch']
            stage1_answers = dict(session['stage1_answers'])
    branch_ids = STAGE2B_HARD_IDS if branch == 'hard' else STAGE2A_EASY_IDS
    ans_map = validate_answers(request.all_answers, STAGE1_MEDIUM_IDS + branch_ids)
    if any(ans_map[q] != stage1_answers[q] for q in STAGE1_MEDIUM_IDS):
        raise HTTPException(status_code=400, detail='Stage 1 answers differ from the routed answers.')

    triplets = []
    correct_count = 0

    for q, sel_idx in ans_map.items():
        q_data = get_full_question_data(q)
        is_corr = 1 if sel_idx == q_data["correct_answer_index"] else 0
        if is_corr:
            correct_count += 1
        triplets.append((0, q, is_corr))

    adaptest_data = AdapTestDataset(triplets, concept_map, 1, total_questions, total_concepts, 20)
    adaptest_data.reset2()
    for q in ans_map.keys():
        adaptest_data.apply_selection(0, q)

    model = init_ncd_evaluator(tau=0.0)
    model.init_model(adaptest_data)
    model.adaptest_load(CKPT_PATH)
    model.update(adaptest_data, out=False)

    with torch.no_grad():
        device = model.model.student_emb.weight.device
        sid = torch.tensor([0], dtype=torch.long, device=device)
        mastery_vec = torch.sigmoid(model.model.student_emb(sid))[0].cpu().numpy()

    # Phân loại câu hỏi theo Listening (Part 1-4) và Reading (Part 5-7)
    listen_items = [q for q in ans_map.keys() if int(catalog_df[catalog_df["q_idx"] == q].iloc[0]["part"]) <= 4]
    read_items = [q for q in ans_map.keys() if int(catalog_df[catalog_df["q_idx"] == q].iloc[0]["part"]) >= 5]

    corr_listen = sum(1 for q in listen_items if ans_map[q] == get_full_question_data(q)["correct_answer_index"])
    corr_read = sum(1 for q in read_items if ans_map[q] == get_full_question_data(q)["correct_answer_index"])

    # NCD mastery on assessed Part concepts, with raw evidence counts.
    part_summary = []
    for p in range(1, 8):
        p_items = [q for q in ans_map.keys() if int(catalog_df[catalog_df["q_idx"] == q].iloc[0]["part"]) == p]
        p_q_cnt = len(p_items)
        p_assessed = (p_q_cnt > 0)
        p_corr_cnt = sum(1 for q in p_items if ans_map[q] == get_full_question_data(q)["correct_answer_index"])
        
        if p_assessed:
            p_latent = float(mastery_vec[p - 1])
            p_score_pct = round(p_latent * 100, 1)
        else:
            p_score_pct = None

        part_summary.append({
            "part": p,
            "part_name": f"Part {p}",
            "is_assessed": p_assessed,
            "question_count": p_q_cnt,
            "correct_count": p_corr_cnt,
            "score_pct": p_score_pct,
            "measure": "ncd_mastery_index",
        })

    # Danh sách 24 kỹ năng NCD (Radar)
    radar_skills = []
    for c_idx in range(total_concepts):
        c_items = [q for q in ans_map.keys() if c_idx in concept_map[q]]
        c_q_cnt = len(c_items)
        c_assessed = (c_q_cnt > 0)
        c_corr_cnt = sum(1 for q in c_items if ans_map[q] == get_full_question_data(q)["correct_answer_index"])
        name = concept_names.get(c_idx, f"Skill {c_idx+1}")

        if c_assessed:
            c_latent = float(mastery_vec[c_idx])
            c_score_pct = round(c_latent * 100, 1)
        else:
            c_score_pct = None

        radar_skills.append({
            "concept_idx": c_idx,
            "concept_name": name,
            "is_assessed": c_assessed,
            "question_count": c_q_cnt,
            "correct_count": c_corr_cnt,
            "score_pct": c_score_pct,
            "measure": "ncd_mastery_index",
        })

    assessed_skills = [s for s in radar_skills if s["question_count"] >= 3 and s["score_pct"] is not None]
    sorted_assessed = sorted(assessed_skills, key=lambda s: s["score_pct"], reverse=True)
    strengths = [s for s in sorted_assessed if s["score_pct"] >= 65][:3]
    weaknesses = [s for s in sorted_assessed[::-1] if s["score_pct"] < 60][:3]

    return {
        "user_id": request.user_id,
        "question_source": "separate_live_question_bank",
        "paper_source": PAPER_SOURCE,
        "routed_branch": branch,
        "accuracy_pct": round(correct_count / 20 * 100, 1),
        "correct_answers": correct_count,
        "correct_listening": corr_listen,
        "correct_reading": corr_read,
        "total_questions": 20,
        "diagnostic_measure": "NCD mastery index on assessed concepts; not a TOEIC score",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "part_summary": part_summary,
        "radar_skills": radar_skills
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting PCAT + NCD FastAPI Server on http://127.0.0.1:8000 ...")
    uvicorn.run("pcat_server:app", host="127.0.0.1", port=8000, reload=False)
