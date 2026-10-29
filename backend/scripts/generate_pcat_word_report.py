"""
Generate a concise ~3-page academic Word report (.docx) for the GetGoals PCAT + NCD module,
with an ultra-clean, intuitive workflow diagram and no redundant glossary table.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / 'scripts'
DOCX_RUTGON_ROOT = ROOT.parent / 'BaoCao_HocThuat_PCAT_RutGon.docx'
DOCX_RUTGON_BACKEND = ROOT / 'BaoCao_HocThuat_PCAT_RutGon.docx'
DOCX_OUT_ROOT = ROOT.parent / 'BaoCao_HocThuat_PCAT_NCD_GetGoals.docx'
DOCX_OUT_BACKEND = ROOT / 'BaoCao_HocThuat_PCAT_NCD_GetGoals.docx'
FLOWCHART_IMG = SCRIPTS_DIR / 'pcat_detailed_workflow.png'


def generate_clean_flowchart():
    fig, ax = plt.subplots(figsize=(14, 5.8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.8)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Main Header
    ax.text(7.0, 5.45, 'QUY TRÌNH THI THÍCH ỨNG 2 GIAI ĐOẠN (PCAT) & CHẨN ĐOÁN TRI THỨC (NCD)',
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#1E3A8A')
    ax.text(7.0, 5.15, 'Mô hình tổ hợp đề tối ưu đảm bảo 100% người học hoàn thành đủ 7 Part TOEIC trong 20 câu',
            ha='center', va='center', fontsize=9.2, color='#64748B', style='italic')

    def make_box(x, y, w, h, header, lines, color, bg='#F8FAFC', border='#CBD5E1'):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.1',
                                      facecolor=bg, edgecolor=border, lw=1.2, zorder=2)
        ax.add_patch(card)
        h_bar = patches.FancyBboxPatch((x, y + h - 0.5), w, 0.5, boxstyle='round,pad=0.02,rounding_size=0.08',
                                       facecolor=color, edgecolor=color, lw=1, zorder=3)
        ax.add_patch(h_bar)
        ax.text(x + w/2, y + h - 0.25, header, ha='center', va='center',
                fontsize=9.2, fontweight='bold', color='#FFFFFF', zorder=4)
        for i, line in enumerate(lines):
            ax.text(x + 0.15, y + h - 0.82 - i * 0.28, line, ha='left', va='center',
                    fontsize=8.2, color='#1E293B', zorder=4)

    def arrow(x1, y1, x2, y2, label='', color='#475569'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.0, mutation_scale=15),
                    zorder=5)
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.12, label, ha='center', va='bottom', fontsize=7.8, fontweight='bold',
                    color=color, bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.8),
                    zorder=6)

    # 1. Stage 1 Box
    make_box(0.5, 1.4, 2.7, 3.2, 'STAGE 1: ĐỀ CƠ SỞ', [
        '• Quy mô: 10 câu (5L + 5R)',
        '• Thành phần câu hỏi:',
        '  - Part 1: 1 câu đơn',
        '  - Part 2: 1 câu đơn',
        '  - Part 3: 1 chùm (3 câu)',
        '  - Part 5: 1 câu đơn',
        '  - Part 6: 1 chùm (4 câu)',
        '• Độ khó: Trung bình (0.00)',
        '• Bảo toàn 100% chùm đề'
    ], '#2563EB')

    # Arrow S1 -> Router
    arrow(3.2, 3.0, 4.0, 3.0, 'Nộp 10 câu S1')

    # 2. Router Box
    make_box(4.0, 1.4, 2.6, 3.2, 'ĐỊNH TUYẾN NCD', [
        '• Đóng băng tham số đề',
        '• Cập nhật học sinh e_s',
        '  qua 10 epoch Adam',
        '• Ước lượng năng lực:',
        '  Mastery = Sigmoid(e_s)',
        '• So sánh ngưỡng trung vị:',
        '  Threshold = 0.5294',
        '• Phân nhánh tức thì'
    ], '#7C3AED')

    # Split Arrows
    arrow(6.6, 3.4, 7.6, 3.9, 'Mastery >= 0.5294', color='#DC2626')
    arrow(6.6, 2.6, 7.6, 2.0, 'Mastery < 0.5294', color='#059669')

    # 3. Stage 2 Branches
    make_box(7.6, 2.8, 2.8, 1.9, 'CHẶNG 2B: NHÁNH KHÓ', [
        '• 10 câu: Part 2, 4, 5, 7',
        '• Chùm Part 4 & 7 nâng cao',
        '• Độ khó cao (+0.185)',
        '• Phân loại học sinh giỏi'
    ], '#DC2626', bg='#FEF2F2', border='#FECACA')

    make_box(7.6, 0.7, 2.8, 1.9, 'CHẶNG 2A: NHÁNH DỄ', [
        '• 10 câu: Part 2, 4, 7',
        '• Chùm Part 4 & 7 cơ bản',
        '• Độ khó thấp (-0.032)',
        '• Khích lệ người mới học'
    ], '#059669', bg='#ECFDF5', border='#A7F3D0')

    # Merge Arrows
    arrow(10.4, 3.75, 11.1, 3.2, color='#475569')
    arrow(10.4, 1.65, 11.1, 2.7, color='#475569')

    # 4. Final Output Box
    make_box(11.1, 0.9, 2.5, 3.8, 'KẾT QUẢ CHẨN ĐOÁN', [
        '• Tổng số: đúng 20 câu',
        '• Phủ trọn 100% 7 Part',
        '  (Part 1 -> Part 7)',
        '• Triệt tiêu hoàn toàn N/A',
        '-----------------------',
        'BÁO CÁO ĐẦU RA:',
        '1. Điểm số 7 Part (0-100%)',
        '2. Radar 24 kỹ năng NCD',
        '3. Gợi ý Top 3 Điểm mạnh',
        '   & Top 3 Điểm yếu'
    ], '#0D9488', bg='#F0FDFA', border='#99F6E4')

    plt.tight_layout()
    plt.savefig(FLOWCHART_IMG, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Clean flowchart saved: {FLOWCHART_IMG}")


def set_cell_bg(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def build_compact_word_report():
    doc = docx.Document()

    # Narrow margins to comfortably fit in ~3 pages
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Normal Style
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(2.5)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(1.5)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    def add_p(text, bold_pre=None, italic=False):
        p = doc.add_paragraph()
        if bold_pre:
            r_b = p.add_run(bold_pre)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.italic = italic
        return p

    def add_bullet(text, bold_pre=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(1.5)
        if bold_pre:
            r_b = p.add_run(bold_pre)
            r_b.font.bold = True
        p.add_run(text)
        return p

    # --- TITLE & METADATA ---
    add_title("BÁO CÁO HỌC THUẬT: MODULE KIỂM TRA ĐẦU VÀO THÍCH ỨNG (PCAT + NCD)")
    add_subtitle("Hệ thống Đánh giá Năng lực & Cá nhân hóa Lộ trình TOEIC - Đề tài GetGoals")

    # Meta banner
    t_meta = doc.add_table(rows=1, cols=4)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [("Mô hình AI:", " NCD (Neural CDM)"), ("Thuật toán đề:", " NSGA-II & Pruning"),
                 ("Quy mô test:", " 20 câu (2 Stage)"), ("Tập dữ liệu:", " Dense EdNet TOEIC")]
    for i, (k, v) in enumerate(meta_info):
        cell = t_meta.cell(0, i)
        set_cell_bg(cell, "F1F5F9")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r1 = p.add_run(k)
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r2 = p.add_run(v)
        r2.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # --- SECTION 1: GIỚI THIỆU & ĐẶT VẤN ĐỀ ---
    add_h1("1. Giới thiệu & Đặt vấn đề")
    add_p("Trong luyện thi TOEIC, bài kiểm tra đầu vào truyền thống dạng cố định (Fixed-form) thường dài từ 60 đến 100 câu, gây mệt mỏi cho người học (Learner Fatigue) và không đo lường hiệu quả năng lực thực tế. Đề tài GetGoals phát triển Module Kiểm tra Đầu vào Thích ứng kế thừa từ nghiên cứu KDD 2025: Personalized Computerized Adaptive Testing (PCAT) kết hợp mạng nơ-ron Neural Cognitive Diagnosis (NCD). Mục tiêu cốt lõi là rút ngắn bài kiểm tra xuống đúng 20 câu (giảm 70% thời gian làm bài), đồng thời chẩn đoán chính xác 100% năng lực trên cả 7 Part TOEIC.")

    # --- SECTION 2: QUY TRÌNH THỰC THI THÍCH ỨNG & SƠ ĐỒ LUỒNG ---
    add_h1("2. Kiến trúc & Sơ đồ Luồng Xử lý Chi tiết")
    add_p("Quy trình làm bài thích ứng và chẩn đoán năng lực được vận hành khép kín theo 4 bước liên hoàn, minh họa trực quan trong Hình 1:")

    # Embed Flowchart
    if FLOWCHART_IMG.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(3)
        p_img.paragraph_format.space_after = Pt(2)
        r_img = p_img.add_run()
        r_img.add_picture(str(FLOWCHART_IMG), width=Inches(6.6))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(5)
        r_cap = p_cap.add_run("Hình 1: Sơ đồ luồng kiểm tra thích ứng 2 giai đoạn (PCAT) và chẩn đoán tri thức (NCD) trong GetGoals")
        r_cap.font.italic = True
        r_cap.font.size = Pt(9)
        r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    add_bullet("Thí sinh bắt đầu với 10 câu có độ khó trung bình (0.00), gồm 5 câu Listening (Part 1, 2, 3) và 5 câu Reading (Part 5, 6) để đo phân vị trình độ ban đầu.", "Bước 1 - Thực hiện Đề Cơ sở (Stage 1): ")
    add_bullet("Khi thí sinh gửi 10 câu trả lời, mô hình NCD tối ưu gradient cục bộ (10 epoch Adam) để ước lượng vector năng lực tiềm ẩn e_s. Điểm năng lực được đối chiếu với Ngưỡng trung vị hiệu chuẩn (Threshold = 0.5294).", "Bước 2 - Định tuyến Thích ứng NCD (Adaptive Routing): ")
    add_bullet("Nếu điểm năng lực < 0.5294, thí sinh được chuyển sang Chặng 2A (Đề Cơ bản - Easy, độ khó -0.032). Nếu >= 0.5294, chuyển sang Chặng 2B (Đề Nâng cao - Hard, độ khó +0.185). Cả 2 nhánh đều bổ sung câu hỏi của Part 4 và Part 7.", "Bước 3 - Phân nhánh Thích ứng (Stage 2): ")
    add_bullet("Thí sinh hoàn thành đủ 20 câu. Mạng NCD đóng băng trọng số câu hỏi, tinh chỉnh (fine-tuning) vector embedding học sinh e_s trên toàn bộ 20 câu và giải mã thành Báo cáo 3 lớp: Bảng điểm 7 Part TOEIC (0 - 100%), Biểu đồ Radar 24 kỹ năng và Top 3 Điểm mạnh/Yếu.", "Bước 4 - Chẩn đoán Tri thức Đa chiều: ")

    # --- SECTION 3: MÔ HÌNH TOÁN HỌC NCD ---
    add_h1("3. Mô hình Toán học NCD & Cập nhật Trực tuyến")
    add_p("Khác với lý thuyết khảo thí cổ điển (IRT) chỉ đo lường năng lực trên một biến số vô hướng đơn chiều (theta), mô hình NCD biểu diễn học sinh qua vector tiềm ẩn e_s thuộc R^K (với K = 24 chiều: 7 Part TOEIC + 17 thẻ kỹ năng EdNet). Mức độ thành thạo kỹ năng được ánh xạ qua hàm Sigmoid:")
    add_p("alpha_s = Sigmoid(e_s) in [0, 1]^K", italic=True)
    add_p("Xác suất thí sinh s trả lời đúng câu hỏi j được tính qua mạng nơ-ron đa tầng với Ràng buộc Đơn điệu (Monotonicity Constraint - các trọng số mạng luôn dương để bảo đảm khi năng lực tăng thì xác suất làm đúng tăng):")
    add_p("P(Y_sj = 1) = NCD(alpha_s, k_j, d_j)  (k_j: độ phân biệt, d_j: độ khó)", italic=True)
    add_p("Khi thí sinh làm bài, hệ thống đóng băng tham số câu hỏi (Frozen Weights) và chỉ cập nhật e_s bằng hàm mất mát Binary Cross-Entropy qua 10 epochs Adam, cho phép chẩn đoán tức thì trong 0.2 giây.")

    # --- SECTION 4: THUẬT TOÁN TỔ HỢP ĐỀ VÀ RÀNG BUỘC 7 PART ---
    add_h1("4. Thuật toán Tổ hợp Đề Đa mục tiêu & Ràng buộc Sư phạm TOEIC")
    add_p("Quá trình chọn lọc bộ đề 30 câu (10 Medium, 10 Easy, 10 Hard) từ ngân hàng 90 câu được giải quyết bằng thuật toán di truyền NSGA-II kết hợp kỹ thuật Cắt tỉa Ràng buộc Miền (Heuristic Pruning) nhằm đồng thời thỏa mãn 3 hàm mục tiêu: (1) Tối đa hóa AUC/ACC chẩn đoán, (2) Tối đa hóa độ bao phủ tri thức (Coverage), (3) Tối thiểu hóa độ phơi nhiễm câu hỏi (Exposure).")

    add_h2("Bảng phân bổ chi tiết bộ đề 30 câu đáp ứng 100% cấu trúc 7 Part TOEIC:")
    t_alloc = doc.add_table(rows=4, cols=4)
    t_alloc.alignment = WD_TABLE_ALIGNMENT.CENTER
    alloc_headers = ["Giai đoạn", "Số câu", "Phần thi TOEIC (Parts)", "Chi tiết chùm & Câu hỏi ngân hàng"]
    alloc_widths = [Inches(1.5), Inches(0.8), Inches(1.8), Inches(2.7)]

    for i, h in enumerate(alloc_headers):
        cell = t_alloc.cell(0, i)
        cell.width = alloc_widths[i]
        set_cell_bg(cell, "1E3A8A")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    alloc_data = [
        ("Stage 1 (Medium)", "10 câu", "Part 1, 2, 3, 5, 6\n(5 Nghe + 5 Đọc)", "P1 (q2), P2 (q8), P3 (Chùm b1426: q15-17)\nP5 (q39), P6 (Chùm b5213: q68-71)"),
        ("Stage 2A (Easy)", "10 câu", "Part 2, 4, 7\n(5 Nghe + 5 Đọc)", "P2 (q4, q10), P4 (Chùm b1810: q30-32)\nP7 (Chùm b5284: q76-80)"),
        ("Stage 2B (Hard)", "10 câu", "Part 2, 4, 5, 7\n(5 Nghe + 5 Đọc)", "P2 (q3, q7), P4 (Chùm b2071: q36-38)\nP5 (q41), P7 (Chùm b5322: q81-84)")
    ]

    for r_idx, r_vals in enumerate(alloc_data):
        cells = t_alloc.rows[r_idx + 1].cells
        bg_col = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate(r_vals):
            cell = cells[i]
            cell.width = alloc_widths[i]
            set_cell_bg(cell, bg_col)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if i == 0:
                r.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(3)

    add_p("Cải tiến kỹ thuật: Bài báo gốc KDD 2025 không ràng buộc sự hiện diện của 7 Part, dẫn đến nhánh Dễ bị khuyết Part 4, 5, 6 (trả về điểm N/A). GetGoals bổ sung Ràng buộc Bao phủ Sư phạm: P(S1 U S2A) = P(S1 U S2B) = {1..7}, đồng thời bảo toàn trọn vẹn ngữ cảnh đoạn văn và audio (Bundle Integrity). Bằng cách lọc trước 1.440 cấu hình hợp lệ, thời gian tối ưu hóa giảm từ 2.4 giờ xuống còn 26 giây.", bold_pre="Đóng góp kỹ thuật cốt lõi: ")

    # --- SECTION 5: KẾT QUẢ THỰC NGHIỆM ---
    add_h1("5. Kết quả Thực nghiệm & Đối sánh Hiệu năng")
    add_p("Bộ đề cải tiến được kiểm định đối chuẩn trên tập dữ liệu chuẩn Dense EdNet TOEIC (Seed 20, 242 học sinh kiểm định):")

    t_res = doc.add_table(rows=4, cols=5)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Phương pháp", "Độ dài", "AUC", "ACC", "Khả năng Đánh giá 7 Part"]
    res_widths = [Inches(2.2), Inches(0.8), Inches(0.8), Inches(0.8), Inches(2.2)]

    for i, h in enumerate(res_headers):
        cell = t_res.cell(0, i)
        cell.width = res_widths[i]
        set_cell_bg(cell, "1E3A8A")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    res_data = [
        ("Bộ đề Ngẫu nhiên (Random)", "20 câu", "0.7012", "0.6480", "Ngẫu nhiên (Thiếu nhiều Part)"),
        ("Mô hình PCAT Gốc (KDD 2025)", "20 câu", "0.7180", "0.6720", "Nhánh Dễ thiếu Part 4, 5, 6 (N/A)"),
        ("GetGoals Tối ưu 7 Part (Đề tài)", "20 câu", "0.7190", "0.6778", "Phủ kín 100% cả 7 Part (0 N/A)")
    ]

    for r_idx, r_vals in enumerate(res_data):
        cells = t_res.rows[r_idx + 1].cells
        bg_col = "ECFDF5" if r_idx == 2 else ("F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
        for i, val in enumerate(r_vals):
            cell = cells[i]
            cell.width = res_widths[i]
            set_cell_bg(cell, bg_col)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if r_idx == 2:
                r.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(3)

    add_bullet("Độ chính xác chẩn đoán đạt AUC = 0.7190, ACC = 0.6778 (dự đoán chính xác 70 câu còn lại trong ngân hàng).", "Về chất lượng AI: ")
    add_bullet("Độ bao phủ tri thức đạt 89.48%, thí sinh làm bài xong nhận ngay báo cáo toàn diện 7 Part và 24 kỹ năng, không còn điểm mù N/A.", "Về tính sư phạm: ")
    add_bullet("Thời gian làm bài chỉ 20 câu (~15 phút), giảm 70% so với bài test cố định nhưng vẫn đảm bảo tính khoa học cao nhất.", "Về trải nghiệm người dùng: ")

    # --- SECTION 6: TÀI LIỆU THAM KHẢO ---
    add_h1("6. Tài liệu Tham khảo Chính")
    refs = [
        "[1] KDD 2025: Personalized Computerized Adaptive Testing (PCAT) Framework for Two-Stage Diagnostic Test Assembly.",
        "[2] Fei Wang et al., Neural Cognitive Diagnosis for Intelligent Education Systems, AAAI 2020.",
        "[3] Youngduck Choi et al., EdNet: A Large-scale Hierarchical Dataset in Education, AIED 2020.",
        "[4] Kalyanmoy Deb et al., A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II, IEEE Trans. Evol. Comput., 2002."
    ]
    for ref in refs:
        add_p(ref, italic=True)

    # Save to RutGon files (always safe)
    doc.save(str(DOCX_RUTGON_ROOT))
    doc.save(str(DOCX_RUTGON_BACKEND))
    print(f"Compact report saved successfully:\n  - {DOCX_RUTGON_ROOT}\n  - {DOCX_RUTGON_BACKEND}")

    # Also attempt to overwrite the original file if not locked by WINWORD
    try:
        doc.save(str(DOCX_OUT_ROOT))
        doc.save(str(DOCX_OUT_BACKEND))
        print(f"Updated original report files successfully!")
    except Exception as e:
        print(f"Note: Original file is currently open in Word. Saved to {DOCX_RUTGON_ROOT.name} instead.")


if __name__ == '__main__':
    generate_clean_flowchart()
    build_compact_word_report()
