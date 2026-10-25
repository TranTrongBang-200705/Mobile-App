import os
import sys
import json
import torch
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from dataset.adaptest_dataset import AdapTestDataset
from pcat_server import (
    STAGE1_MEDIUM_IDS, ROUTING_THRESHOLD, CKPT_PATH,
    init_ncd_evaluator, concept_map, total_questions, total_concepts,
    get_full_question_data, catalog_df, concept_names
)

print(f"=== KHẢO SÁT GIẢ LẬP PHÂN NHÁNH THÍ SINH CÙNG ĐÚNG 5/10 CÂU (CHẶNG 1) ===")
print(f"Ngưỡng phân nhánh (Routing Threshold): {ROUTING_THRESHOLD:.4f} ({ROUTING_THRESHOLD*100:.2f}%)")
print(f"Danh sách 10 câu Chặng 1: {STAGE1_MEDIUM_IDS}\n")

# Thí sinh 1: Đúng 5 câu Reading (Part 7: 85, 86, 87, 88, 89), sai 5 câu Listening
# Thí sinh 2: Đúng 5 câu Listening (Part 1, 2, 3: 24, 25, 26, 12, 1), sai 5 câu Reading
# Thí sinh 3: Đúng chùm câu khó / kỹ năng cao
# Thí sinh 4: Đúng rải rác các câu đơn lẻ

patterns = {
    "Thí sinh 1 (Chuyên Đọc hiểu: Đúng 5 câu Part 7, sai toàn bộ Listening)": [85, 86, 87, 88, 89],
    "Thí sinh 2 (Chuyên Nghe hiểu: Đúng 5 câu Part 1, 2, 3, sai toàn bộ Reading)": [24, 25, 26, 12, 1],
    "Thí sinh 3 (Tổ hợp C: Đúng Part 1 + Part 2 + 3 câu Part 7: [1, 12, 85, 86, 87])": [1, 12, 85, 86, 87],
    "Thí sinh 4 (Tổ hợp D: Đúng Part 3 + 2 câu Part 7: [24, 25, 26, 88, 89])": [24, 25, 26, 88, 89],
    "Thí sinh 5 (Tổ hợp E: Đúng 1 câu Nghe [1] + 4 câu Đọc [85, 86, 87, 88])": [1, 85, 86, 87, 88],
    "Thí sinh 6 (Tổ hợp F: Đúng 4 câu Nghe [24, 25, 26, 12] + 1 câu Đọc [89])": [24, 25, 26, 12, 89],
}

medium_concepts = sorted({c for q in STAGE1_MEDIUM_IDS for c in concept_map[q]})

results = []

for name, correct_set in patterns.items():
    triplets = []
    for q in STAGE1_MEDIUM_IDS:
        is_corr = 1 if q in correct_set else 0
        triplets.append((0, q, is_corr))
    
    adaptest_data = AdapTestDataset(triplets, concept_map, 1, total_questions, total_concepts, 20)
    adaptest_data.reset2()
    for q in STAGE1_MEDIUM_IDS:
        adaptest_data.apply_selection(0, q)
        
    model = init_ncd_evaluator(tau=0.0)
    model.init_model(adaptest_data)
    model.adaptest_load(CKPT_PATH)
    model.update(adaptest_data, out=False)
    
    with torch.no_grad():
        device = model.model.student_emb.weight.device
        sid = torch.tensor([0], dtype=torch.long, device=device)
        mastery_all = torch.sigmoid(model.model.student_emb(sid))[0].cpu().numpy()
        mastery_medium = float(mastery_all[medium_concepts].mean())
        
    branch = "CHẶNG 2B (HARD)" if mastery_medium >= ROUTING_THRESHOLD else "CHẶNG 2A (EASY)"
    diff = mastery_medium - ROUTING_THRESHOLD
    
    # Lấy top kỹ năng radar assessed
    assessed_concepts = [c for c in medium_concepts]
    skill_scores = [(concept_names.get(c, f"Skill {c}"), float(mastery_all[c])) for c in assessed_concepts]
    skill_scores.sort(key=lambda x: x[1], reverse=True)
    
    results.append({
        "name": name,
        "correct_set": correct_set,
        "mastery_score": mastery_medium,
        "branch": branch,
        "diff": diff,
        "top_skills": skill_scores[:3],
        "lowest_skills": skill_scores[-3:],
    })

for idx, r in enumerate(results, 1):
    print(f"----------------------------------------------------------------------")
    print(f"👤 {r['name']}")
    print(f"   * Số câu đúng: 5/10 (50.0%)")
    print(f"   * Các câu làm đúng: {r['correct_set']}")
    print(f"   * Điểm năng lực NCD: {r['mastery_score']:.4f} ({r['mastery_score']*100:.2f}%)")
    print(f"   * So với ngưỡng ({ROUTING_THRESHOLD*100:.2f}%): {r['diff']*100:+.2f}%")
    print(f"   * KẾT QUẢ PHÂN NHÁNH: ===> {r['branch']} <===")
    print(f"   * Radar kỹ năng cao nhất: {', '.join([f'{s[0]} ({s[1]*100:.1f}%)' for s in r['top_skills']])}")
    print(f"   * Radar kỹ năng thấp nhất: {', '.join([f'{s[0]} ({s[1]*100:.1f}%)' for s in r['lowest_skills']])}")
