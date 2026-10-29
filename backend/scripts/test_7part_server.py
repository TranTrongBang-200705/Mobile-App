import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from pcat_server import app, get_full_question_data

client = TestClient(app)

def run_tests():
    print("Testing Easy Route...")
    # 1. Start test via /api/pcat/stage1
    resp = client.get('/api/pcat/stage1')
    assert resp.status_code == 200, resp.text
    start_data = resp.json()
    session_id = start_data['session_id']
    stage1_qs = start_data['questions']
    print(f"Start test OK! Session ID: {session_id}, Stage 1 count: {len(stage1_qs)}")

    # 2. Route with wrong answers -> should route to Easy
    answers_s1_wrong = [{'q_idx': q['q_idx'], 'selected_answer_index': (get_full_question_data(q['q_idx'])['correct_answer_index'] + 1) % 4} for q in stage1_qs]
    route_resp = client.post('/api/pcat/route', json={'session_id': session_id, 'stage1_answers': answers_s1_wrong})
    assert route_resp.status_code == 200, route_resp.text
    route_data = route_resp.json()
    assert route_data['routed_branch'] == 'easy', f"Expected easy, got {route_data['routed_branch']}"
    stage2_easy = route_data['stage2_questions']
    print(f"Routed to: {route_data['routed_branch']}, Stage 2 count: {len(stage2_easy)}")

    # 3. Diagnose Easy path
    answers_s2 = [{'q_idx': q['q_idx'], 'selected_answer_index': get_full_question_data(q['q_idx'])['correct_answer_index']} for q in stage2_easy]
    diag_resp = client.post('/api/pcat/diagnose', json={'session_id': session_id, 'all_answers': answers_s1_wrong + answers_s2})
    assert diag_resp.status_code == 200, diag_resp.text
    diag_data = diag_resp.json()

    print("\n--- Easy Route Part Summary ---")
    all_7_easy = True
    for p in diag_data['part_summary']:
        print(f"  {p['part_name']}: assessed={p['is_assessed']}, q_cnt={p['question_count']}, corr={p['correct_count']}, score={p['score_pct']}%")
        if not p['is_assessed'] or p['score_pct'] is None:
            all_7_easy = False
    assert all_7_easy, "Easy path failed to assess all 7 parts!"
    print(">>> EASY PATH 7/7 PARTS VERIFIED!")

    print("\nTesting Hard Route...")
    # 4. Start test again for Hard route
    resp = client.get('/api/pcat/stage1')
    start_data = resp.json()
    session_id2 = start_data['session_id']
    stage1_qs2 = start_data['questions']

    # Route with 100% correct answers -> should route to Hard
    answers_s1_correct = [{'q_idx': q['q_idx'], 'selected_answer_index': get_full_question_data(q['q_idx'])['correct_answer_index']} for q in stage1_qs2]
    route_resp2 = client.post('/api/pcat/route', json={'session_id': session_id2, 'stage1_answers': answers_s1_correct})
    assert route_resp2.status_code == 200, route_resp2.text
    route_data2 = route_resp2.json()
    assert route_data2['routed_branch'] == 'hard', f"Expected hard, got {route_data2['routed_branch']}"
    stage2_hard = route_data2['stage2_questions']
    print(f"Routed to: {route_data2['routed_branch']}, Stage 2 count: {len(stage2_hard)}")

    # 5. Diagnose Hard path
    answers_s2_hard = [{'q_idx': q['q_idx'], 'selected_answer_index': get_full_question_data(q['q_idx'])['correct_answer_index']} for q in stage2_hard]
    diag_resp2 = client.post('/api/pcat/diagnose', json={'session_id': session_id2, 'all_answers': answers_s1_correct + answers_s2_hard})
    assert diag_resp2.status_code == 200, diag_resp2.text
    diag_data2 = diag_resp2.json()

    print("\n--- Hard Route Part Summary ---")
    all_7_hard = True
    for p in diag_data2['part_summary']:
        print(f"  {p['part_name']}: assessed={p['is_assessed']}, q_cnt={p['question_count']}, corr={p['correct_count']}, score={p['score_pct']}%")
        if not p['is_assessed'] or p['score_pct'] is None:
            all_7_hard = False
    assert all_7_hard, "Hard path failed to assess all 7 parts!"
    print(">>> HARD PATH 7/7 PARTS VERIFIED!")

    print("\nRadar skills count:", len(diag_data2['radar_skills']))
    print(f"Overall Accuracy: {diag_data2['accuracy_pct']}% (L={diag_data2['correct_listening']}/10, R={diag_data2['correct_reading']}/10)")
    print("\nALL PCAT END-TO-END TESTS PASSED WITH 100% SUCCESS!")

if __name__ == '__main__':
    run_tests()
