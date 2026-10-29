"""
Script to generate the comprehensive academic Word report (.docx) with embedded
detailed workflow diagrams for the GetGoals PCAT + NCD module.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / 'scripts'
DOCX_OUT_ROOT = ROOT.parent / 'BaoCao_HocThuat_PCAT_NCD_GetGoals.docx'
DOCX_OUT_BACKEND = ROOT / 'BaoCao_HocThuat_PCAT_NCD_GetGoals.docx'
FLOWCHART_IMG = SCRIPTS_DIR / 'pcat_detailed_workflow.png'

# -------------------------------------------------------------
# STEP 1: GENERATE DETAILED ARCHITECTURE FLOWCHART
# -------------------------------------------------------------
def generate_flowchart():
    fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Color Palette
    c_primary = '#1E3A8A'    # Deep Blue
    c_stage1 = '#2563EB'     # Royal Blue
    c_router = '#7C3AED'     # Purple
    c_easy = '#059669'       # Emerald Green
    c_hard = '#DC2626'       # Deep Red
    c_ncd = '#D97706'        # Amber/Gold
    c_output = '#0D9488'     # Teal
    c_card_bg = '#FFFFFF'
    c_border = '#CBD5E1'

    def draw_box(x, y, w, h, title, subtitle, color, text_color='#FFFFFF', sub_color='#E2E8F0', rx=0.08):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.02,rounding_size={rx}",
            facecolor=color, edgecolor=color, linewidth=1.5, zorder=2
        )
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w / 2, y + h * 0.62, title, ha='center', va='center',
                    fontsize=10.5, fontweight='bold', color=text_color, zorder=3)
            ax.text(x + w / 2, y + h * 0.28, subtitle, ha='center', va='center',
                    fontsize=8.5, color=sub_color, zorder=3)
        else:
            ax.text(x + w / 2, y + h / 2, title, ha='center', va='center',
                    fontsize=10.5, fontweight='bold', color=text_color, zorder=3)

    def draw_card(x, y, w, h, title, lines, header_color, bg_color='#FFFFFF'):
        card = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=bg_color, edgecolor=c_border, linewidth=1.2, zorder=2
        )
        ax.add_patch(card)
        # Header banner
        header = patches.FancyBboxPatch(
            (x, y + h - 0.5), w, 0.5,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=header_color, edgecolor=header_color, linewidth=1, zorder=3
        )
        ax.add_patch(header)
        ax.text(x + w / 2, y + h - 0.25, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=4)
        
        # Text lines
        for i, line in enumerate(lines):
            ax.text(x + 0.2, y + h - 0.8 - i * 0.32, line, ha='left', va='center',
                    fontsize=8.2, color='#334155', zorder=4)

    def draw_arrow(x1, y1, x2, y2, label="", color='#64748B', style='simple'):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=color, lw=2, mutation_scale=15),
            zorder=5
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.15, label, ha='center', va='bottom',
                    fontsize=8, fontweight='bold', color=color,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.8),
                    zorder=6)

    # 1. Main Title
    ax.text(7.5, 10.4, "LUỒNG KIỂM TRA THÍCH ỨNG 2 GIAI ĐOẠN (PCAT) & CHẨN ĐOÁN TRI THỨC (NCD)",
            ha='center', va='center', fontsize=14, fontweight='bold', color=c_primary)
    ax.text(7.5, 10.05, "Mô hình tổ hợp đề tối ưu phủ kín 7 Part TOEIC - Tích hợp trong Hệ thống GetGoals",
            ha='center', va='center', fontsize=10, color='#64748B', style='italic')

    # 2. Stage 1 Box
    draw_card(1.0, 6.8, 4.0, 2.7, "GIAI ĐOẠN 1: ĐỀ CƠ SỞ (MEDIUM)", [
        "• Độ dài: 10 câu (5 Listening + 5 Reading)",
        "• Phủ các phần: Part 1 (1c), Part 2 (1c)",
        "  Part 3 (Chùm b1426: 3c), Part 5 (1c)",
        "  Part 6 (Chùm b5213: 4c)",
        "• Mục tiêu: Đo lường phân vị năng lực ban đầu",
        "• Đảm bảo 100% toàn vẹn chùm audio/đoạn văn"
    ], c_stage1)

    # 3. Routing Engine Box
    draw_card(5.8, 6.8, 3.4, 2.7, "BỘ ĐỊNH TUYẾN THÍCH ỨNG (NCD)", [
        "• Tối ưu 10 epoch Adam cục bộ",
        "• Ước lượng vector: e_s -> alpha_s",
        "• Tính điểm thuần thục: Mastery Index",
        "• So sánh ngưỡng trung vị hiệu chuẩn:",
        "    Threshold = 0.5294 (Seed 20)",
        "• Ra quyết định chuyển nhánh tức thì"
    ], c_router)

    # Arrows Stage 1 -> Router
    draw_arrow(5.0, 8.15, 5.8, 8.15, label="Nộp 10 câu S1")

    # 4. Stage 2 Branches
    draw_card(10.0, 7.8, 4.0, 2.1, "CHẶNG 2A: NHÁNH CƠ BẢN (EASY)", [
        "• Điều kiện: Mastery < 0.5294 (Nửa dưới)",
        "• 10 câu: Part 2 (2c), Part 4 (Chùm b1810: 3c)",
        "  Part 7 (Chùm b5284: 5c)",
        "• Phân tầng: Độ khó trung bình thấp (-0.032)"
    ], c_easy)

    draw_card(10.0, 5.0, 4.0, 2.1, "CHẶNG 2B: NHÁNH NÂNG CAO (HARD)", [
        "• Điều kiện: Mastery >= 0.5294 (Nửa trên)",
        "• 10 câu: Part 2 (2c), Part 4 (Chùm b2071: 3c)",
        "  Part 7 (Chùm b5322: 4c), Part 5 (1c)",
        "• Phân tầng: Độ khó trung bình cao (+0.185)"
    ], c_hard)

    # Routing Arrows
    draw_arrow(9.2, 8.5, 10.0, 8.85, label="Mastery < 0.5294", color=c_easy)
    draw_arrow(9.2, 7.5, 10.0, 6.05, label="Mastery >= 0.5294", color=c_hard)

    # 5. Full 20-Item Aggregator
    draw_card(5.5, 3.1, 4.0, 1.8, "TỔNG HỢP BÀI THI 20 CÂU", [
        "• Tập hợp: S1 + S2A hoặc S1 + S2B",
        "• Phủ kín 100% cả 7 Part TOEIC (1, 2, 3, 4, 5, 6, 7)",
        "• Cân bằng chuẩn: 10 Listening + 10 Reading",
        "• Triệt tiêu hoàn toàn câu hỏi bị khuyết (0 N/A)"
    ], c_primary)

    draw_arrow(10.0, 8.5, 9.5, 4.0, color='#64748B')
    draw_arrow(10.0, 5.5, 9.5, 3.8, color='#64748B')

    # 6. Deep Diagnostic NCD Engine
    draw_card(0.8, 3.1, 4.0, 1.8, "ĐỘNG CƠ CHẨN ĐOÁN TRI THỨC NCD", [
        "• Đóng băng tham số câu hỏi (difficulty d_j)",
        "• Cập nhật Student Latent Embedding e_s",
        "• Ánh xạ qua hàm Sigmoid: alpha_s in [0, 1]^24",
        "• Khớp trực tiếp 24 chiều ma trận Q-matrix"
    ], c_ncd)

    draw_arrow(5.5, 4.0, 4.8, 4.0, label="20 câu trả lời")

    # 7. Final Diagnostic Outputs
    draw_card(1.5, 0.4, 12.0, 2.0, "KẾT QUẢ CHẨN ĐOÁN & CÁ NHÂN HÓA LỘ TRÌNH (GETGOALS OUTPUT)", [
        "1. Đánh giá 7 Part TOEIC: Tỷ lệ thuần thục (Mastery Index 0 - 100%) và số câu đúng/tổng câu cho từng Part 1 đến Part 7 đầy đủ.",
        "2. Biểu đồ Radar 24 Kỹ năng NCD: Định lượng độ vững vàng trên 17 thẻ ngữ pháp/từ vựng vi mô (từ loại, liên từ, thì, suy luận đọc hiểu...).",
        "3. Đề xuất Sư phạm Thông minh: Nhận diện tự động Top 3 Điểm mạnh và Top 3 Điểm yếu để làm đầu vào xây dựng Lộ trình học thích ứng."
    ], c_output)

    draw_arrow(2.8, 3.1, 2.8, 2.4, label="Trích xuất chỉ số", color=c_output)

    plt.tight_layout()
    plt.savefig(FLOWCHART_IMG, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Flowchart image generated at: {FLOWCHART_IMG}")


# -------------------------------------------------------------
# STEP 2: BUILD WORD DOCUMENT WITH DETAILED GLOSSARY & SECTIONS
# -------------------------------------------------------------
def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def create_word_report():
    doc = docx.Document()

    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper functions
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(16)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    def add_p(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.italic = italic
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        return p

    # --- TITLE ---
    add_title("BÁO CÁO HỌC THUẬT: MODULE KIỂM TRA ĐẦU VÀO THÍCH ỨNG (PCAT + NCD)")
    add_subtitle("Hệ thống Đánh giá Năng lực & Luyện thi TOEIC Cá nhân hóa - Đề tài GetGoals")

    # Metadata box
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        [("Hệ thống:", " GetGoals Mobile App & PCAT AI Engine"), ("Mô hình cốt lõi:", " NCD (Neural Cognitive Diagnosis)")],
        [("Thuật toán tổ hợp đề:", " NSGA-II & Domain Constraint Pruning"), ("Dữ liệu thực nghiệm:", " EdNet TOEIC (Dense 90-Item Benchmark)")]
    ]
    for r_idx, row in enumerate(meta_table.rows):
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, "F1F5F9")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            lbl, val = meta_data[r_idx][c_idx]
            r1 = p.add_run(lbl)
            r1.font.bold = True
            r1.font.size = Pt(10)
            r2 = p.add_run(val)
            r2.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 1: GIỚI THIỆU & ĐẶT VẤN ĐỀ ---
    add_h1("1. Giới thiệu & Đặt vấn đề nghiên cứu")
    add_p("Trong quá trình học và luyện thi chứng chỉ TOEIC, việc xác định chính xác trình độ xuất phát và các lỗ hổng kiến thức của người học là bước tiền đề mang tính quyết định. Các phương pháp kiểm tra truyền thống thường áp dụng bài thi có cấu trúc cố định (Fixed-form testing) với số lượng câu hỏi lớn (thường từ 60 đến 100 câu, kéo dài 60–90 phút). Điều này dẫn đến hai nhược điểm nghiêm trọng:")
    add_bullet("Gây mệt mỏi và suy giảm động lực học tập (Learner Fatigue): Người học, đặc biệt là những người mới bắt đầu, dễ nản lòng khi phải làm một bài kiểm tra quá dài.", "Thứ nhất: ")
    add_bullet("Hiệu quả đo lường kém: Các câu hỏi quá dễ hoặc quá khó so với trình độ thực tế của thí sinh không mang lại nhiều thông tin thống kê để chẩn đoán năng lực.", "Thứ hai: ")
    add_p("Để giải quyết bài toán trên, đề tài GetGoals xây dựng Module Kiểm tra Đầu vào Thích ứng (Adaptive Diagnostic Module) kế thừa và phát triển từ công trình khoa học công bố tại KDD 2025: Personalized Computerized Adaptive Testing (PCAT) kết hợp với Mô hình Chẩn đoán Tri thức Nơ-ron (Neural Cognitive Diagnosis - NCD). Mục tiêu tối thượng của module là: Rút ngắn số lượng câu hỏi làm bài xuống chỉ còn 20 câu (giảm 70% thời gian làm bài), nhưng vẫn bảo đảm chẩn đoán toàn diện và chính xác năng lực trên toàn bộ 7 Part của bài thi TOEIC.")

    # --- SECTION 2: BẢNG GIẢI THÍCH THUẬT NGỮ CHUYÊN NGÀNH ---
    add_h1("2. Bảng Giải thích Thuật ngữ Chuyên ngành (Glossary)")
    add_p("Nhằm bảo đảm tính minh xác khoa học và giúp hội đồng phản biện dễ dàng theo dõi, bảng dưới đây tổng hợp và giải thích chi tiết các thuật ngữ nền tảng được sử dụng trong hệ thống:")

    terms_data = [
        ("CAT", "Computerized Adaptive Testing", "Kiểm tra Thích ứng Máy tính: Hình thức kiểm tra mà độ khó của câu hỏi tiếp theo được điều chỉnh tự động theo thời gian thực dựa trên câu trả lời trước đó của thí sinh."),
        ("PCAT", "Personalized Computerized Adaptive Testing", "Kiểm tra Thích ứng Cá nhân hóa: Mô hình CAT hiện đại (KDD 2025) thiết kế cấu trúc bài thi 2 giai đoạn (Two-Stage) kết hợp thuật toán tối ưu đa mục tiêu để cân bằng độ dài bài thi và độ chính xác chẩn đoán."),
        ("NCD", "Neural Cognitive Diagnosis", "Chẩn đoán Tri thức Nơ-ron: Mô hình trí tuệ nhân tạo dùng mạng nơ-ron đa tầng thay thế lý thuyết IRT cổ điển, chẩn đoán mức độ thuần thục đa chiều của học sinh trên từng kỹ năng cụ thể."),
        ("Q-Matrix", "Ma trận Liên kết Câu hỏi - Kỹ năng", "Ma trận nhị phân kích thước (Số câu hỏi x Số kỹ năng). Q[j, k] = 1 nếu câu hỏi j yêu cầu kỹ năng k để giải quyết và bằng 0 nếu ngược lại."),
        ("IRT", "Item Response Theory", "Lý thuyết Ứng đáp Câu hỏi: Mô hình toán học cổ điển ước lượng năng lực học sinh qua một tham số vô hướng theta. Hạn chế là giả định đơn chiều, không chẩn đoán được đa kỹ năng."),
        ("Monotonicity Constraint", "Ràng buộc Tính đơn điệu", "Quy tắc toán học trong mạng NCD: Trọng số của mạng luôn dương, bảo đảm khi mức độ thuần thục kỹ năng của học sinh tăng lên thì xác suất làm đúng câu hỏi cũng tăng theo."),
        ("Student Latent Embedding", "Vector Embedding Năng lực Tiềm ẩn (e_s)", "Vector không gian tiềm ẩn của học sinh e_s thuộc R^K. Sau khi đi qua hàm kích hoạt Sigmoid, thu được vector năng lực alpha_s thuộc [0, 1]^K biểu thị độ thuần thục từng kỹ năng."),
        ("NSGA-II", "Non-dominated Sorting Genetic Algorithm II", "Thuật toán Di truyền Sắp xếp Không bị Thống trị: Thuật toán tối ưu hóa đa mục tiêu mô phỏng tiến hóa sinh học, tìm tập nghiệm tối ưu Pareto giữa các mục tiêu mâu thuẫn."),
        ("Pareto Frontier", "Đường biên Tối ưu Pareto", "Tập hợp các giải pháp tối ưu mà ở đó không một mục tiêu nào có thể cải thiện thêm mà không làm giảm sút một mục tiêu khác."),
        ("Item Exposure Rate", "Tỷ lệ Phơi nhiễm Câu hỏi", "Tần suất một câu hỏi xuất hiện trên tổng số lượt thi. Kiểm soát chỉ số này giúp tránh việc một vài câu hỏi bị lặp lại quá nhiều gây lộ đề thi."),
        ("Bundle Integrity", "Tính Toàn vẹn Chùm câu hỏi", "Quy tắc bảo đảm các câu hỏi chia sẻ chung một bài đọc (Part 6, 7) hoặc đoạn âm thanh (Part 3, 4) luôn được đưa vào cùng nhau, không bị xé lẻ."),
        ("Routing Threshold", "Ngưỡng Phân nhánh Thích ứng", "Giá trị ranh giới (trung vị) dùng để quyết định sau Giai đoạn 1 thí sinh sẽ được chuyển sang nhánh Đề Dễ (Stage 2A) hay Đề Khó (Stage 2B)."),
        ("AUC / ACC", "Area Under ROC Curve / Accuracy", "Chỉ số đo lường độ chính xác chẩn đoán: AUC (độ phân biệt giữa đúng và sai) và ACC (tỷ lệ dự đoán chính xác câu trả lời của thí sinh trên các câu hỏi còn lại)."),
        ("Concept Coverage", "Độ bao phủ Tri thức (Coverage)", "Tỷ lệ phần trăm các khái niệm/kỹ năng trong cây tri thức TOEIC được bài thi kiểm tra thực tế (hệ thống đạt 89.48%).")
    ]

    glossary_table = doc.add_table(rows=len(terms_data) + 1, cols=3)
    glossary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    glossary_table.autofit = False

    # Header Row
    headers = ["Thuật ngữ", "Tên tiếng Anh đầy đủ", "Định nghĩa & Ý nghĩa học thuật"]
    widths = [Inches(1.2), Inches(1.8), Inches(3.5)]
    for i, h in enumerate(headers):
        cell = glossary_table.cell(0, i)
        cell.width = widths[i]
        set_cell_background(cell, "1E3A8A")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Data Rows
    for r_idx, (t_name, t_en, t_desc) in enumerate(terms_data):
        row_cells = glossary_table.rows[r_idx + 1].cells
        bg_col = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate([t_name, t_en, t_desc]):
            cell = row_cells[i]
            cell.width = widths[i]
            set_cell_background(cell, bg_col)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            run.font.size = Pt(9.5)
            if i == 0:
                run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 3: KIẾN TRÚC HỆ THỐNG & SƠ ĐỒ LUỒNG XỬ LÝ ---
    add_h1("3. Kiến trúc Hệ thống & Sơ đồ Luồng Xử lý Chi tiết")
    add_p("Quy trình kiểm tra thích ứng và chẩn đoán năng lực trong GetGoals được tổ chức thành một chu trình khép kín gồm 5 giai đoạn liên kết chặt chẽ. Sơ đồ kiến trúc luồng dữ liệu được minh họa chi tiết trong Hình 1:")

    # Insert Image
    if FLOWCHART_IMG.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(FLOWCHART_IMG), width=Inches(6.2))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run("Hình 1: Sơ đồ luồng xử lý chi tiết của Module Kiểm tra Thích ứng (PCAT) và Động cơ Chẩn đoán Tri thức (NCD)")
        r_cap.font.italic = True
        r_cap.font.size = Pt(10)
        r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    add_h2("Chi tiết 5 bước trong luồng xử lý của hệ thống:")
    add_p("Hệ thống khởi tạo một phiên làm bài duy nhất (Session-based) có thời gian sống (TTL). Thí sinh nhận đề Giai đoạn 1 gồm 10 câu hỏi có độ khó trung bình (Medium), trong đó cân bằng chính xác 5 câu Listening (Part 1: 1 câu, Part 2: 1 câu, Part 3: 1 chùm 3 câu) và 5 câu Reading (Part 5: 1 câu, Part 6: 1 chùm 4 câu).", "Bước 1 - Khởi tạo phiên & Thực hiện Đề Cơ sở (Stage 1): ")
    add_p("Khi thí sinh gửi 10 câu trả lời của Stage 1 lên endpoint /api/pcat/route, Động cơ NCD khởi tạo vector embedding học sinh e_s và tối ưu hóa gradient qua 10 epochs (Adam, lr=0.05). Điểm năng lực tiềm ẩn trung bình được đối chiếu với Ngưỡng phân nhánh (Threshold = 0.5294).", "Bước 2 - Phân tích Thích ứng & Định tuyến NCD (Adaptive Routing): ")
    add_p("Dựa trên kết quả định tuyến: Nếu điểm thuần thục < 0.5294, thí sinh được chuyển sang Chặng 2A (Đề Cơ bản - Easy, độ khó -0.032). Nếu điểm thuần thục >= 0.5294, thí sinh được chuyển sang Chặng 2B (Đề Nâng cao - Hard, độ khó +0.185). Cả hai nhánh đều bổ sung các câu hỏi của Part 4 và Part 7.", "Bước 3 - Thực hiện Giai đoạn 2 Phân tầng (Stage 2): ")
    add_p("Thí sinh hoàn tất tổng cộng 20 câu hỏi và gửi lên endpoint /api/pcat/diagnose. Mạng NCD đóng băng toàn bộ trọng số câu hỏi và thực hiện cập nhật mịn (Fine-tuning) vector năng lực e_s trên toàn bộ 20 tương tác thực tế.", "Bước 4 - Cập nhật Trực tuyến Mô hình NCD (Online Fine-Tuning): ")
    add_p("Hệ thống giải mã vector alpha_s thành báo cáo năng lực 3 lớp: Bảng điểm 7 Part TOEIC, Biểu đồ Radar 24 kỹ năng và Top 3 Điểm mạnh/Điểm yếu để phục vụ thuật toán cá nhân hóa lộ trình học.", "Bước 5 - Kết xuất Báo cáo Chẩn đoán Đa chiều: ")

    # --- SECTION 4: THUẬT TOÁN TỔ HỢP ĐỀ ĐA MỤC TIÊU ---
    add_h1("4. Thuật toán Tổ hợp Đề Đa mục tiêu & Ràng buộc Sư phạm TOEIC")
    add_p("Quá trình tổ hợp bộ đề 30 câu (10 Medium, 10 Easy, 10 Hard) từ ngân hàng 90 câu được giải quyết như một bài toán Tối ưu hóa Đa mục tiêu có ràng buộc khắt khe:")

    add_h2("a. Các hàm mục tiêu toán học:")
    add_bullet("Tối đa hóa diện tích dưới đường cong ROC và độ chính xác dự đoán của NCD trên tập 242 học sinh kiểm định.", "Mục tiêu 1 (f1 - Maximize Diagnostic Accuracy): ")
    add_bullet("Tối đa hóa tỷ lệ các khái niệm trong ma trận Q-matrix được bài thi chạm tới (đạt 89.48%).", "Mục tiêu 2 (f2 - Maximize Concept Coverage): ")
    add_bullet("Tối thiểu hóa độ lệch chuẩn tần suất xuất hiện của các câu hỏi nhằm bảo đảm an toàn đề thi.", "Mục tiêu 3 (f3 - Minimize Item Exposure): ")

    add_h2("b. Hệ thống 4 Ràng buộc Sư phạm Cải tiến:")
    add_bullet("Các câu hỏi thuộc cùng một đoạn hội thoại (Part 3, 4) hoặc bài đọc (Part 6, 7) tuyệt đối không bị tách rời.", "1. Ràng buộc Bảo toàn Chùm (Bundle Integrity): ")
    add_bullet("Mỗi giai đoạn 10 câu luôn có đúng 5 câu Nghe và 5 câu Đọc, bảo đảm cấu trúc cân đối của đề TOEIC.", "2. Ràng buộc Cân bằng Nghe - Đọc: ")
    add_bullet("Cả lộ trình Dễ (S1 + S2A) và lộ trình Khó (S1 + S2B) đều bảo đảm có mặt đầy đủ từ Part 1 đến Part 7, khắc phục triệt để nhược điểm thiếu Part (N/A) của bài báo gốc.", "3. Ràng buộc Bao phủ Toàn diện 7 Part: ")
    add_bullet("Độ khó trung bình đo lường bởi NCD bảo đảm thứ tự nghiêm ngặt: Diff(Stage 2A) = -0.032 < Diff(Stage 1) = -0.000 < Diff(Stage 2B) = +0.185.", "4. Ràng buộc Phân tầng Độ khó: ")

    add_h2("c. Đóng góp Kỹ thuật: Heuristic Constraint Pruning")
    add_p("Trong mã nguồn gốc của bài báo, thuật toán NSGA-II phải chạy qua 100 thế hệ ngẫu nhiên, mất 2.4 giờ (8.612 giây). Đề tài GetGoals đã áp dụng kỹ thuật Cắt tỉa Không gian Ràng buộc (Heuristic Constraint Pruning): Nhận diện các đơn vị bất biến (54 chùm đề), sàng lọc trước các tổ hợp vi phạm ràng buộc sư phạm để chỉ còn 1.440 cấu hình hợp lệ, sau đó đưa vào hàm Fitness NCD đánh giá trực tiếp. Kỹ thuật này giúp tìm ra bộ đề tối ưu tuyệt đối chỉ trong 26 giây mà chất lượng mô hình tương đương hoàn toàn.")

    # --- SECTION 5: KẾT QUẢ THỰC NGHIỆM & ĐÁNH GIÁ HIỆU NĂNG ---
    add_h1("5. Kết quả Thực nghiệm & So sánh Đối chuẩn")
    add_p("Hiệu năng của bộ đề tối ưu 7 Part trong GetGoals được đánh giá đối chuẩn (Benchmark) với các phương pháp khác trên tập dữ liệu chuẩn Dense EdNet TOEIC (Seed 20):")

    bench_data = [
        ("Bộ đề Ngẫu nhiên (Random Baseline)", "20 câu", "0.7012", "0.6480", "72.40%", "Ngẫu nhiên (Thiếu nhiều Part)"),
        ("Mô hình PCAT Gốc (KDD 2025)", "20 câu", "0.7180", "0.6720", "85.20%", "Thiếu Part 4, 5, 6 ở nhánh Dễ (N/A)"),
        ("Mô hình GetGoals Cải tiến (Đề tài)", "20 câu", "0.7190", "0.6778", "89.48%", "Phủ trọn 100% cả 7 Part (0 N/A)")
    ]

    bench_table = doc.add_table(rows=len(bench_data) + 1, cols=6)
    bench_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    bench_headers = ["Phương pháp", "Độ dài test", "AUC", "ACC", "Độ phủ (Coverage)", "Khả năng Đánh giá 7 Part"]
    bench_widths = [Inches(1.8), Inches(0.8), Inches(0.7), Inches(0.7), Inches(1.1), Inches(1.8)]

    for i, h in enumerate(bench_headers):
        cell = bench_table.cell(0, i)
        cell.width = bench_widths[i]
        set_cell_background(cell, "1E3A8A")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row_vals in enumerate(bench_data):
        row_cells = bench_table.rows[r_idx + 1].cells
        bg_col = "ECFDF5" if r_idx == 2 else ("F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
        for i, val in enumerate(row_vals):
            cell = row_cells[i]
            cell.width = bench_widths[i]
            set_cell_background(cell, bg_col)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            run.font.size = Pt(9)
            if r_idx == 2:
                run.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    add_h2("Nhận xét học thuật:")
    add_bullet("Bộ đề tối ưu của đề tài đạt AUC = 0.7190 và ACC = 0.6778, vượt trội so với baseline ngẫu nhiên và nhỉnh hơn bản gốc KDD 2025.", "Độ chính xác chẩn đoán: ")
    add_bullet("Đạt 89.48% (tăng hơn 4% so với mô hình gốc), bảo đảm cây tri thức được đo lường sâu rộng nhất.", "Độ bao phủ tri thức: ")
    add_bullet("Khắc phục hoàn toàn bài toán 'điểm mù' kỹ năng, tạo ra một trải nghiệm khảo thí toàn diện và đáng tin cậy cho ứng dụng GetGoals.", "Tính thực tiễn khảo thí: ")

    # --- SECTION 6: TÀI LIỆU THAM KHẢO ---
    add_h1("6. Tài liệu Tham khảo Chính (References)")
    refs = [
        "[1] KDD 2025: Personalized Computerized Adaptive Testing (PCAT) Framework for Two-Stage Diagnostic Test Assembly.",
        "[2] Fei Wang et al., Neural Cognitive Diagnosis for Intelligent Education Systems, In Proceedings of the AAAI Conference on Human Computation and Crowdsourcing (AAAI 2020).",
        "[3] Youngduck Choi et al., EdNet: A Large-scale Hierarchical Dataset in Education, AIED 2020.",
        "[4] Kalyanmoy Deb et al., A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II, IEEE Transactions on Evolutionary Computation, 2002.",
        "[5] Wim J. van der Linden, Elements of Adaptive Testing, Springer Statistics for Social and Behavioral Sciences, 2010."
    ]
    for ref in refs:
        add_p(ref, italic=True)

    # Save to both paths
    doc.save(str(DOCX_OUT_ROOT))
    doc.save(str(DOCX_OUT_BACKEND))
    print(f"Report saved to:\n  - {DOCX_OUT_ROOT}\n  - {DOCX_OUT_BACKEND}")

if __name__ == '__main__':
    generate_flowchart()
    create_word_report()
