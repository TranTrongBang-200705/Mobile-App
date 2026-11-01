"""
Build the focused academic Word report concentrating specifically on the TWO CORE PHASES,
with explicit parameter breakdowns, inputs/outputs, bilingual terminology (Vietnamese in parentheses),
and full mathematical/pedagogical interpretations of every quantity.
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / 'scripts'
FLOWCHART_IMG = SCRIPTS_DIR / 'pcat_ncd_comprehensive_workflow.png'

# Output paths
DOCX_COTLOI_ROOT = ROOT.parent / 'BaoCao_PCAT_NCD_2Pha_CotLoi.docx'
DOCX_COTLOI_BACKEND = ROOT / 'BaoCao_PCAT_NCD_2Pha_CotLoi.docx'
DOCX_TOANDIEN_ROOT = ROOT.parent / 'BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx'
DOCX_TOANDIEN_BACKEND = ROOT / 'BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx'
DOCX_FINAL_ROOT = ROOT.parent / 'BaoCao_PCAT_NCD_GetGoals_Final.docx'
DOCX_FINAL_BACKEND = ROOT / 'BaoCao_PCAT_NCD_GetGoals_Final.docx'
DOCX_RUTGON_ROOT = ROOT.parent / 'BaoCao_HocThuat_PCAT_RutGon.docx'


def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def build_focused_report():
    doc = docx.Document()

    # Page Margins: 0.8 inch for clean layout
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Text styling helpers
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x76, 0x6E)

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    def add_p(text, bold_pre=None, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            rb = p.add_run(bold_pre)
            rb.font.name = 'Times New Roman'
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.italic = italic
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_bullet(text, bold_pre=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_pre:
            rb = p.add_run(bold_pre)
            rb.font.name = 'Times New Roman'
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_math_para(omml_str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        xml = f'<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMath>{omml_str}</m:oMath></m:oMathPara>'
        p._p.append(parse_xml(xml))
        return p

    def add_callout(text, bold_title="ĐIỂM CỐT LÕI: "):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.8)
        set_cell_bg(cell, "EFF6FF")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(bold_title)
        r1.font.name = 'Times New Roman'
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
        r2 = p.add_run(text)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ------------------ TITLE & OVERVIEW ------------------
    add_title("BÁO CÁO KỸ THUẬT CHUYÊN SÂU:\nHAI PHA VẬN HÀNH CỐT LÕI CỦA HỆ THỐNG PCAT-NCD")
    add_subtitle("Mối quan hệ Phối hợp NCD – NSGA-II: Phân tách Input, Output, Bộ tham số và Ý nghĩa Đại lượng Toán học (GetGoals TOEIC)")

    # Metadata Table
    t_meta = doc.add_table(rows=1, cols=4)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [("Mô hình AI:", " NCD (Neural CDM)"),
                 ("Thuật toán Đề:", " NSGA-II & Pruning"),
                 ("Tập Dữ liệu:", " Dense EdNet TOEIC (K=24)"),
                 ("Quy mô Test:", " 20 câu (2 Stage Thích ứng)")]
    for i, (k, v) in enumerate(meta_info):
        cell = t_meta.cell(0, i)
        set_cell_bg(cell, "F1F5F9")
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(k)
        r1.font.name = 'Times New Roman'
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r2 = p.add_run(v)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # TỔNG QUAN VỀ QUAN HỆ "AI CHẠY TRƯỚC - AI CHẠY SAU"
    add_h2("TỔNG QUAN: BẢN CHẤT QUAN HỆ 'AI CHẠY TRƯỚC - AI CHẠY SAU' GIỮA NCD VÀ NSGA-II")
    add_callout(
        "Quy tắc vàng trong hệ thống GetGoals:\n"
        "1. NCD là 'Cây thước đo năng lực' (Evaluator/Surrogate Model): Bắt buộc phải được huấn luyện (pre-train) TRƯỚC trên tập dữ liệu EdNet để học toàn bộ thuộc tính câu hỏi (độ khó d_j, độ phân biệt k_j, trọng số đơn điệu W).\n"
        "2. NSGA-II là 'Người thợ tổ hợp tìm kiếm đề' (Search Optimizer): Chạy THỨ HAI, sinh ra các bộ đề 30 câu ứng viên và gọi cây thước đo NCD chấm điểm độ chính xác AUC/Coverage để tiến hóa chọn lọc tự nhiên.\n"
        "3. Khi phát hành lên Mobile App cho thí sinh thi thật: Bộ đề 30 câu đã chốt cố định trong cơ sở dữ liệu. Thuật toán NSGA-II NGHỈ HOÀN TOÀN (để người dùng không phải chờ đợi chạy tiến hóa). Duy nhất mô hình NCD vận hành trực tuyến trong thời gian thực (< 30 mili-giây) để chấm bài, rẽ nhánh và vẽ biểu đồ Radar.",
        bold_title="BẢN CHẤT VẬN HÀNH: "
    )

    # Embed Flowchart
    if FLOWCHART_IMG.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r_img = p_img.add_run()
        r_img.add_picture(str(FLOWCHART_IMG), width=Inches(6.8))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(6)
        r_cap = p_cap.add_run("Hình 1: Sơ đồ luồng hai pha vận hành cốt lõi: Pha 1 Offline (NCD làm Giám khảo <-> NSGA-II tổ hợp đề) và Pha 2 Online (NCD thi thích ứng trực tuyến trên App)")
        r_cap.font.name = 'Times New Roman'
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)
        r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # =========================================================================
    # PHẦN 1: PHA TỐI ƯU HÓA OFFLINE
    # =========================================================================
    add_h1("PHẦN 1: PHA TỐI ƯU HÓA OFFLINE (NCD HUẤN LUYỆN TRƯỚC LÀM GIÁM KHẢO ⟷ NSGA-II TỔ HỢP ĐỀ 30 CÂU & HIỆU CHUẨN NGƯỠNG)")
    add_p("Pha Offline được thực hiện một lần duy nhất trước khi phát hành hệ thống lên môi trường thực tế, gồm 4 mắt xích liên hoàn:")

    # 1.1 NCD Pre-training
    add_h2("1.1. Bước 1: Huấn luyện NCD Trước trên Tập dữ liệu EdNet (NCD Pre-training)")
    add_p("Bản chất & Mục tiêu: Muốn đánh giá một câu hỏi TOEIC là Khó hay Dễ, phân loại giỏi/kém thế nào, hệ thống phải học từ dữ liệu lịch sử. NCD chạy đầu tiên trên tập dữ liệu chuẩn hóa Dense_EdNetTOEIC_Balanced90_90d gồm tổng cộng 303 học sinh (27.270 tương tác đầy đủ 100% trên 90 câu hỏi cân bằng 7 Parts và 24 kỹ năng tri thức), được phân chia theo tỷ lệ chuẩn 80/20: 242 học sinh tập Train và 61 học sinh tập Test (Hold-out). NCD học các thuộc tính câu hỏi để làm 'cây thước đo chuẩn' cho NSGA-II.", bold_pre="Vai trò: ")

    add_bullet("Ma trận Quan hệ Câu hỏi - Kỹ năng (Q-matrix / Question-Skill Incidence Matrix) kích thước 90 x 24: q_jk = 1 nếu câu hỏi j kiểm tra kỹ năng k; ngược lại q_jk = 0. Tệp nhật ký làm bài lịch sử TotalData.csv của 242 học sinh tập huấn luyện (Training Cohort - chiếm 80% trong 303 học sinh): gồm các bộ 3 (s, j, y_sj) với y_sj ∈ {0, 1} (1: làm đúng, 0: làm sai). 61 học sinh còn lại (20%) được giữ lại làm tập kiểm thử độc lập (Hold-out Test).", "Input (Đầu vào khi Huấn luyện Offline): ")
    add_bullet("Tệp điểm lưu trọng số mô hình đã học xong (Trained Checkpoint): model_Dense_EdNetTOEIC_Balanced90_90d_seed20_train_ncd.pt đóng gói toàn bộ tham số câu hỏi d_j, k_j, W_1, W_2, b_1, b_2 cố định để làm cây thước đo chuyển giao cho NSGA-II.", "Output 1 (Đầu ra của Pha Huấn luyện Offline - Training Output): ")
    add_bullet("Khi nạp file .pt lên Mobile App để học sinh làm bài thực tế, đầu ra của NCD được chuyển đổi thành: (1) Vector độ thuần thục 24 kỹ năng α_s = σ(e_s) để vẽ BIỂU ĐỒ RADAR và (2) Điểm năng lực tổng quát θ_bar để PHÂN CHẶNG 2A/2B (chi tiết tại Phần 2).", "Output 2 (Đầu ra của Pha Kiểm tra Thực tế - Online Inference Output): ")

    add_p("Bảng Giải mã Bộ Tham số (Parameters) và Ý nghĩa Đại lượng:", bold_pre="Bộ tham số mô hình: ")
    add_bullet("d_j ∈ R^24 (Item Difficulty Vector - Vector độ khó của câu hỏi j): Đại diện cho mức độ phức tạp của câu hỏi j trên từng kỹ năng. Giá trị d_j càng lớn thì câu hỏi đó càng khó, đòi hỏi năng lực thí sinh cao hơn mới làm đúng.", "• Tham số d_j: ")
    add_bullet("k_j ∈ R^24 (Item Discrimination Vector - Vector độ phân biệt của câu hỏi j): Thể hiện khả năng phân tách học sinh giỏi và học sinh yếu. Giá trị k_j càng cao thì câu hỏi càng nhạy, giúp phân loại rạch ròi trình độ thí sinh.", "• Tham số k_j: ")
    add_bullet("W_1 ∈ R^{24 x 16}, W_2 ∈ R^{16 x 1} (Neural Network Weights - Ma trận trọng số mạng tương tác PredictNet): Ràng buộc luôn không âm W_1 ≥ 0, W_2 ≥ 0 (Ràng buộc Đơn điệu / Monotonicity Constraint). Ý nghĩa sư phạm: Bảo đảm nguyên tắc logic - khi năng lực học sinh tăng lên thì xác suất làm đúng câu hỏi luôn tăng hoặc giữ nguyên, tuyệt đối không bao giờ giảm.", "• Tham số W_1, W_2: ")
    add_bullet("b_1, b_2 (Biases - Hệ số chệch): Tham số điều chỉnh ngưỡng kích hoạt nơ-ron.", "• Tham số b_1, b_2: ")

    add_p("Công thức Lan truyền Tiến (Forward Pass) của NCD PredictNet:")
    add_math_para('''
    <m:r><m:t>P(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:t>sj</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> = 1) = σ(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> · ReLU(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>s</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> - </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) ∘ </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>k</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>b</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) + </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>b</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>)</m:t></m:r>
    ''')
    add_bullet("P(Y_sj = 1): Xác suất thí sinh s làm đúng câu hỏi j (nằm trong khoảng [0, 1]).")
    add_bullet("α_s = σ(e_s) ∈ [0, 1]^24 (Skill Mastery Vector - Vector độ thuần thục kỹ năng của học sinh s trên 24 chiều concept).")
    add_bullet("∘ (Tích Hadamard / Hadamard Element-wise Product - phép nhân từng phần tử tương ứng của hai vector).")
    add_bullet("ReLU (Rectified Linear Unit - Hàm chỉnh lưu kích hoạt phi tuyến: ReLU(z) = max(0, z)).")
    add_bullet("σ (Logistic Sigmoid Function - Hàm Sigmoid nén mọi giá trị thực về đoạn [0, 1]: σ(z) = 1 / (1 + e^{-z})).")

    # 1.2 Heuristic Pruning
    add_h2("1.2. Bước 2: Cắt tỉa Không gian Ràng buộc Sư phạm (Heuristic Constraint Pruning)")
    add_p("Bản chất & Mục tiêu: Bài báo gốc KDD 2025 tìm kiếm trên không gian tự do dẫn đến tổ hợp C(90, 30) ≈ 4.1 × 10^23 bùng nổ, tạo ra đề thi bị khuyết Part 4, 5, 6 (trả về điểm N/A) hoặc xé lẻ đoạn văn Part 6, 7. Thuật toán Cắt tỉa Heuristic đóng vai trò 'bộ lọc tiền xử lý' (Pre-filtering Engine) loại bỏ 99.999% các tổ hợp vi phạm.", bold_pre="Vai trò: ")

    add_bullet("Ngân hàng đề M = 90 câu TOEIC kèm siêu dữ liệu (Metadata): Phần thi (Part 1-7), mã chùm câu hỏi (Atomic Bundle ID), vector độ khó d_j.", "Input (Đầu vào chi tiết): ")
    add_bullet("Tập hợp đúng 1.440 cấu hình chùm đề hợp lệ (Feasible Configuration Pool), sẵn sàng nạp cho thuật toán di truyền.", "Output (Đầu ra chi tiết): ")

    add_p("Bốn Luật Ràng buộc Sư phạm Cốt lõi:")
    add_bullet("1. Ràng buộc Bao phủ 7 Part (Full 7-Part Coverage Constraint): Bắt buộc cả 2 nhánh Dễ và Khó khi ghép với Stage 1 đều có mặt đủ 7 Part TOEIC, loại bỏ hoàn toàn điểm mù N/A:")
    add_math_para('''
    <m:r><m:t>𝒫(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> ∪ </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>2A</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) = 𝒫(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> ∪ </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>2B</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) = {1, 2, 3, 4, 5, 6, 7}</m:t></m:r>
    ''')
    add_bullet("2. Cân bằng Nghe - Đọc (Content Balance Constraint): Mỗi stage 10 câu có đúng 5 câu Nghe (Part 1-4) và 5 câu Đọc (Part 5-7).")
    add_bullet("3. Phân tầng Độ khó Thích ứng (Difficulty Hierarchy Constraint): Bảo đảm độ khó trung bình phân tầng rõ rệt: d(S_2A) = -0.032 < d(S_1) = 0.000 < d(S_2B) = +0.185.")
    add_bullet("4. Bảo toàn Chùm câu hỏi (Bundle Integrity Constraint): 100% ngữ cảnh bài đọc Part 6, 7 và audio Part 3, 4 được giữ nguyên vẹn, tuyệt đối không tách rời câu hỏi trong cùng một chùm.")
    add_p("Hiệu năng: Thu hẹp không gian tìm kiếm về 1.440 cấu hình giúp thời gian tối ưu hóa giảm từ 2.4 giờ xuống còn 26 giây.", italic=True)

    # 1.3 NSGA-II
    add_h2("1.3. Bước 3: Thuật toán NSGA-II Tối ưu hóa Bộ đề (NSGA-II Paper Assembly)")
    add_p("Bản chất & Mục tiêu: NSGA-II là Thuật toán Di truyền Đa mục tiêu có lưu trữ cá thể ưu tú (Elitist Multi-Objective Genetic Algorithm). NSGA-II sinh ra các cá thể đề thi x = [S_1, S_2A, S_2B] ∈ ℕ^30 và liên tục gọi cây thước đo NCD (từ Bước 1) qua hàm evaluate() để chấm điểm AUC, hướng quần thể tiến hóa về mặt trận Pareto tối ưu.", bold_pre="Cơ chế phối hợp: ")

    add_bullet("1.440 cấu hình đề hợp lệ (từ Bước 2); Mô hình NCD đã đóng băng tham số (từ Bước 1); Hồ sơ kiểm định của 242 học sinh.", "Input (Đầu vào chi tiết): ")
    add_bullet("Bộ đề tối ưu 30 câu x* (Seed 20) đạt Pareto-optimal: AUC = 0.7190, ACC = 0.6778, Coverage = 89.48% (lưu tại optimized_7part_paper_seed20.json).", "Output (Đầu ra chi tiết): ")

    add_p("Bộ Tham số Thuật toán Di truyền NSGA-II:")
    add_bullet("N = 80 (Population Size - Kích thước quần thể: gồm 80 bộ đề ứng viên cùng tiến hóa).", "• Tham số N: ")
    add_bullet("G = 100 (Generations - Số thế hệ tiến hóa: 100 vòng lặp chọn lọc tự nhiên).", "• Tham số G: ")
    add_bullet("p_c = 0.9 (Crossover Probability - Xác suất lai ghép: 90% cá thể được trao đổi chùm câu hỏi để tạo đề mới).", "• Tham số p_c: ")
    add_bullet("p_m = 0.1 (Mutation Probability - Xác suất đột biến: 10% cơ hội thay thế ngẫu nhiên một chùm câu hỏi bằng chùm tương đương).", "• Tham số p_m: ")

    add_p("Ba Hàm Mục tiêu Pareto Tối ưu Đồng thời:")
    add_math_para('''
    <m:r><m:t>max </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(x) = AUC(x),  max </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(x) = Coverage(x),  min </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>f</m:t></m:r></m:e><m:sub><m:r><m:t>3</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(x) = Exposure(x)</m:t></m:r>
    ''')
    add_bullet("f_1(x) = AUC(x) (Area Under the ROC Curve - Độ chính xác dự đoán AI): Đo mức độ chuẩn xác khi dùng 20 câu trong đề dự đoán kết quả làm bài của 242 học sinh trên 70 câu còn lại. Đạt giá trị 0.7190.")
    add_bullet("f_2(x) = Coverage(x) (Skill Coverage Ratio - Độ bao phủ kỹ năng tri thức): Tỷ lệ các thẻ kỹ năng EdNet được kiểm chứng trong đề thi. Đạt giá trị 89.48% (phủ 19/24 kỹ năng).")
    add_bullet("f_3(x) = Exposure(x) (Item Exposure Overlap - Mức độ phơi nhiễm câu hỏi): Đo độ lệch bình phương tần suất xuất hiện giữa các câu hỏi, bảo đảm mọi câu hỏi đều được phân bổ công bằng, chống thiên vị lộ đề.")

    # 1.4 Median Calibration
    add_h2("1.4. Bước 4: Hiệu chuẩn Ngưỡng Trung vị Phân chặng (Offline Median Calibration)")
    add_p("Bản chất & Mục tiêu: Thuật toán xác định ngưỡng rẽ nhánh khách quan dựa trên phân vị xác suất thực nghiệm, tuyệt đối không đặt ngưỡng theo cảm tính.", bold_pre="Vai trò: ")

    add_bullet("10 câu hỏi Stage 1 (S_1) đã được chốt từ Bước 3; 242 học sinh tập huấn luyện EdNet (N_train = 242).", "Input (Đầu vào chi tiết): ")
    add_bullet("Ngưỡng trung vị hiệu chuẩn bất biến (Frozen Routing Threshold): τ_median = 0.529395 (~0.5294) lưu tại file live_routing_calibration.json.", "Output (Đầu ra chi tiết): ")

    add_p("Quy trình 4 Bước Tính toán Chi tiết con số τ_median = 0.5294:")
    add_bullet("Bước 1: Cho 242 học sinh cùng làm 10 câu Stage 1. Khởi tạo vector năng lực tại mốc 0: e_s = [0, 0, ..., 0] (tương đương Prior = 50%).")
    add_bullet("Bước 2: Mạng NCD chạy 10 epoch Adam cập nhật e_s dựa trên đáp án thực tế của từng học sinh.")
    add_bullet("Bước 3: Tính điểm năng lực trung bình trên các kỹ năng xuất hiện ở Stage 1 (C_S1):")
    add_math_para('''
    <m:r><m:t>Mastery(s, </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) = </m:t></m:r>
    <m:f>
      <m:num><m:r><m:t>1</m:t></m:r></m:num>
      <m:den>
        <m:r><m:t>|</m:t></m:r>
        <m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>S1</m:t></m:r></m:sub></m:sSub>
        <m:r><m:t>|</m:t></m:r>
      </m:den>
    </m:f>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:supHide m:val="1"/></m:naryPr>
      <m:sub>
        <m:r><m:t>k ∈ </m:t></m:r>
        <m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>S1</m:t></m:r></m:sub></m:sSub>
      </m:sub>
      <m:e>
        <m:sSub><m:e><m:r><m:t>α</m:t></m:r></m:e><m:sub><m:r><m:t>sk</m:t></m:r></m:sub></m:sSub>
      </m:e>
    </m:nary>
    ''')
    add_bullet("Bước 4: Thu được danh sách 242 con số thực [0.3821, ..., 0.6892], sắp xếp tăng dần. Lấy giá trị trung vị tại vị trí thứ 121 (0.529362) và thứ 122 (0.529427): τ_median = (0.529362 + 0.529427) / 2 = 0.52939468... làm tròn thành 0.5294. Ngưỡng này chia đều quần thể học sinh chuẩn mực thành đúng 50% Easy và 50% Hard.")

    # =========================================================================
    # PHẦN 2: PHA THI THÍCH ỨNG & CHẨN ĐOÁN ONLINE
    # =========================================================================
    add_h1("PHẦN 2: PHA THI THÍCH ỨNG & CHẨN ĐOÁN ONLINE (THỜI GIAN THỰC TRÊN MOBILE APP - CHỈ NCD VẬN HÀNH)")
    add_p("Khi người dùng mở ứng dụng GetGoals để làm bài kiểm tra: Bộ đề 30 câu đã chốt cố định trong cơ sở dữ liệu. Thuật toán NSGA-II đã hoàn thành nhiệm vụ và NGHỈ HOÀN TOÀN (để người dùng không phải chờ đợi chạy tiến hóa). Toàn bộ tiến trình chỉ do mô hình NCD vận hành trực tuyến trong thời gian thực:")

    # 2.1 Stage 1
    add_h2("2.1. Giai đoạn 1: Thí sinh làm Đề Cơ sở (Stage 1 - 10 câu Medium)")
    add_bullet("Danh sách 10 mã câu hỏi S_1 (5 câu Nghe Part 1, 2, 3 và 5 câu Đọc Part 5, 6); 10 lựa chọn đáp án của thí sinh ans_1, ..., ans_10.", "Input (Đầu vào chi tiết): ")
    add_bullet("Mảng nhị phân đúng/sai y_sj ∈ {0, 1}; Vector năng lực cập nhật e_s; Điểm năng lực Mastery(s, S_1).", "Output (Đầu ra chi tiết): ")

    add_p("Bộ Tham số Thuật toán Tối ưu Trực tuyến (Online Adam Optimizer):")
    add_bullet("e_s^(0) = [0, 0, ..., 0] ∈ R^24 (Prior Baseline - Điểm khởi tạo năng lực ban đầu: Sigmoid(0) = 0.50 tương ứng mốc trung lập 50%).", "• Điểm khởi tạo: ")
    add_bullet("η = 0.002 (Learning Rate - Tốc độ học của thuật toán Adam).", "• Tốc độ học: ")
    add_bullet("β_1 = 0.9, β_2 = 0.999, ε = 1e-8 (Momentum Parameters - Hệ số suy giảm moment bậc 1 và bậc 2).", "• Tham số Adam: ")
    add_bullet("Số epoch = 10 vòng lặp; Kích thước lô (Batch Size) = 1 (xử lý đơn thí sinh trong < 30 mili-giây).", "• Quy mô tối ưu: ")

    add_p("Hàm Mất mát Binary Cross-Entropy (BCE Loss) dùng để tối ưu vector e_s:")
    add_math_para('''
    <m:r><m:t>ℒ(</m:t></m:r>
    <m:sSub><m:e><m:r><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:t>s</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) = - </m:t></m:r>
    <m:nary>
      <m:naryPr><m:chr m:val="∑"/><m:supHide m:val="1"/></m:naryPr>
      <m:sub>
        <m:r><m:t>j ∈ </m:t></m:r>
        <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>tested</m:t></m:r></m:sub></m:sSub>
      </m:sub>
      <m:e>
        <m:r><m:t>[ </m:t></m:r>
        <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>sj</m:t></m:r></m:sub></m:sSub>
        <m:r><m:t> ln P(</m:t></m:r>
        <m:sSub><m:e><m:r><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:t>sj</m:t></m:r></m:sub></m:sSub>
        <m:r><m:t> = 1) + (1 - </m:t></m:r>
        <m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>sj</m:t></m:r></m:sub></m:sSub>
        <m:r><m:t>) ln (1 - P(</m:t></m:r>
        <m:sSub><m:e><m:r><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:t>sj</m:t></m:r></m:sub></m:sSub>
        <m:r><m:t> = 1)) ]</m:t></m:r>
      </m:e>
    </m:nary>
    ''')

    # 2.2 Routing
    add_h2("2.2. Giai đoạn 2: Quyết định Định tuyến Thích ứng Tức thì (< 1ms)")
    add_bullet("Điểm số Mastery(s, S_1) của học sinh s và ngưỡng trung vị hiệu chuẩn τ_median = 0.5294.", "Input: ")
    add_bullet("Quyết định rẽ nhánh: branch = 'hard' (Stage 2B) hoặc branch = 'easy' (Stage 2A).", "Output: ")

    add_p("Quy tắc Phân định Nhánh Thích ứng (Adaptive Routing Function):")
    add_math_para('''
    <m:r><m:t>Branch(s) = </m:t></m:r>
    <m:d><m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/></m:dPr><m:e>
      <m:eqArr>
        <m:e>
          <m:r><m:t>Stage 2B (Hard),  nếu Mastery(s, </m:t></m:r>
          <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
          <m:r><m:t>) ≥ </m:t></m:r>
          <m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>median</m:t></m:r></m:sub></m:sSub>
        </m:e>
        <m:e>
          <m:r><m:t>Stage 2A (Easy),  nếu Mastery(s, </m:t></m:r>
          <m:sSub><m:e><m:r><m:t>S</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>
          <m:r><m:t>) &lt; </m:t></m:r>
          <m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>median</m:t></m:r></m:sub></m:sSub>
        </m:e>
      </m:eqArr>
    </m:e></m:d>
    ''')

    # 2.3 Stage 2
    add_h2("2.3. Giai đoạn 3: Thí sinh làm Đề Phân nhánh (Stage 2 - 10 câu Easy / Hard)")
    add_bullet("Nếu vào Chặng 2A (Easy, độ khó d = -0.032): Làm 10 câu cơ bản gồm Part 2 (2 câu), Part 4 (3 câu) và Part 7 (chùm bài đọc cơ bản 5 câu q76-80). Giúp người học mới bắt đầu không bị quá tải.", "Nhánh Dễ: ")
    add_bullet("Nếu vào Chặng 2B (Hard, độ khó d = +0.185): Làm 10 câu nâng cao gồm Part 2 (2 câu), Part 4 (3 câu), Part 5 (1 câu) và Part 7 (chùm bài đọc nâng cao 4 câu q81-84). Giúp phân loại rõ rệt học sinh giỏi.", "Nhánh Khó: ")
    add_p("Cả hai nhánh đều bổ sung hoàn tất Part 4 và Part 7, bảo đảm người học làm đúng 20 câu là hoàn thành 100% cả 7 Part TOEIC.")

    # 2.4 Diagnostic Report
    add_h2("2.4. Giai đoạn 4: Báo cáo Chẩn đoán Tri thức Đa chiều 3 Lớp (3-Layer Diagnostic Report)")
    add_bullet("Toàn bộ 20 câu hỏi và kết quả làm bài của thí sinh (S_tested = S_1 ∪ S_2).", "Input: ")
    add_bullet("Đối tượng JSON hoàn chỉnh gồm: Bảng điểm 7 Part, Biểu đồ Radar 24 Kỹ năng, Danh sách Top Điểm mạnh/Điểm yếu.", "Output: ")

    add_p("Ba Lớp Chẩn đoán Đầu ra:")
    add_bullet("Lớp 1: Bảng điểm 7 Part TOEIC (0 - 100%): Tỷ lệ làm đúng thô (correct_count / question_count) và Điểm thuần thục NCD (score_pct), khắc phục triệt để điểm mù N/A.")
    add_bullet("Lớp 2: Biểu đồ Radar 24 Kỹ năng NCD: Điểm số của từng kỹ năng được tính bằng ánh xạ Sigmoid: Score(k) = Sigmoid(e_sk) * 100%.")
    add_bullet("Lớp 3: Top 3 Điểm mạnh (Strengths) và Top 3 Điểm yếu (Weaknesses): Lọc các kỹ năng có ít nhất 3 câu kiểm chứng (question_count >= 3); Điểm mạnh nếu score_pct >= 65%, Điểm yếu nếu score_pct < 60%.")

    add_callout(
        "Giải thích vì sao làm đúng 4/4 câu Part 7 lại ra điểm Radar 62.3% mà không phải 100%:\n"
        "1. Tỷ lệ đúng thô (Raw Accuracy) vẫn là 4/4 = 100%.\n"
        "2. Điểm NCD là Năng lực tiềm ẩn α_s = Sigmoid(e_s). Ban đầu e_s = 0 -> Sigmoid(0) = 50% (Prior trung lập). "
        "Qua 10 epoch Adam với 4 câu đúng, gradient kéo e_{s, Part 7} lên +0.502 -> Sigmoid(+0.502) = 62.3%.\n"
        "3. Khoa học Khảo thí (Psychometrics): Không một hệ thống AI nào dám khẳng định học sinh là 'thần đồng tuyệt đối 100%' chỉ sau 4 câu trắc nghiệm (vẫn có xác suất đoán mò 25%). "
        "Con số 62.3% vượt xa trung vị cộng đồng người học (52.94%), phản ánh phân vị xuất sắc trong không gian NCD.",
        bold_title="GIẢI MÃ CON SỐ CỐT LÕI: TẠI SAO 4/4 PART 7 RA 62.3%? "
    )

    # =========================================================================
    # PHẦN 3: HAI KỊCH BẢN ĐỐI CHIẾU THỰC TẾ
    # =========================================================================
    add_h1("PHẦN 3: HAI KỊCH BẢN ĐỐI CHIẾU THỰC TẾ (WALKTHROUGH: THÍ SINH A VS THÍ SINH B)")
    add_p("Bảng đối sánh trực quan quá trình vận hành từ đầu đến cuối giữa 2 thí sinh:")

    t_cmp = doc.add_table(rows=7, cols=4)
    t_cmp.alignment = WD_TABLE_ALIGNMENT.CENTER
    cmp_headers = ["Tiêu chí Khảo thí & Chẩn đoán", "Thí sinh A (Khá - Giỏi)", "Thí sinh B (Cơ bản - Mới bắt đầu)", "Ý nghĩa Toán học & Sư phạm"]
    cmp_widths = [Inches(1.8), Inches(1.5), Inches(1.5), Inches(2.0)]

    for c_idx, h_text in enumerate(cmp_headers):
        cell = t_cmp.cell(0, c_idx)
        cell.width = cmp_widths[c_idx]
        set_cell_bg(cell, "0F766E")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    cmp_data = [
        ("Kết quả Stage 1 (10 câu)", "Đúng 8 / 10 câu", "Đúng 3 / 10 câu", "Đo nhanh phân vị ban đầu trong 10 câu"),
        ("Điểm Mastery(s, S1)", "0.5824", "0.4412", "Trung bình Sigmoid(e_s) trên Stage 1"),
        ("Quyết định Định tuyến", "Stage 2B (Hard - Nâng cao)", "Stage 2A (Easy - Cơ bản)", "So sánh đối chiếu với τ_median = 0.5294"),
        ("Kết quả Part 7 Stage 2", "Đúng 4 / 4 câu (Đề khó)", "Đúng 1 / 5 câu (Đề dễ)", "Phân loại năng lực đọc hiểu chuyên sâu"),
        ("Điểm NCD Part 7", "62.3% (Xuất sắc)", "38.6% (Cần cải thiện)", "Hàm Sigmoid ánh xạ qua 10 epoch Adam"),
        ("Xếp loại trên Mobile App", "Top 1 Điểm mạnh (Strengths)", "Top 1 Điểm yếu (Weaknesses)", "Cơ sở sinh Lộ trình học thích ứng GetGoals")
    ]

    for r_idx, r_vals in enumerate(cmp_data):
        cells = t_cmp.rows[r_idx + 1].cells
        bg_col = "F0FDFA" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(r_vals):
            cells[c_idx].width = cmp_widths[c_idx]
            set_cell_bg(cells[c_idx], bg_col)
            p = cells[c_idx].paragraphs[0]
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Save
    save_targets = [
        ("BaoCao_PCAT_NCD_2Pha_CotLoi.docx (Root)", DOCX_COTLOI_ROOT),
        ("BaoCao_PCAT_NCD_2Pha_CotLoi.docx (Backend)", DOCX_COTLOI_BACKEND),
        ("BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx (Root)", DOCX_TOANDIEN_ROOT),
        ("BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx (Backend)", DOCX_TOANDIEN_BACKEND),
        ("BaoCao_PCAT_NCD_GetGoals_Final.docx (Root)", DOCX_FINAL_ROOT),
        ("BaoCao_PCAT_NCD_GetGoals_Final.docx (Backend)", DOCX_FINAL_BACKEND),
        ("BaoCao_HocThuat_PCAT_RutGon.docx (Root)", DOCX_RUTGON_ROOT),
    ]

    for label, target_path in save_targets:
        try:
            doc.save(str(target_path))
            print(f"  [OK] Saved: {label} -> {target_path}")
        except Exception as e:
            print(f"  [LOCKED/ERROR] Could not save {label}: {e}")


if __name__ == '__main__':
    build_focused_report()
