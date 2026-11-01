"""
Build the focused Word report concentrating specifically on the TWO CORE PHASES:
- PHẦN 1: PHA TỐI ƯU HÓA OFFLINE (NCD TRAIN TRƯỚC LÀM GIÁM KHẢO <-> NSGA-II TỔ HỢP ĐỀ 30 CÂU & HIỆU CHUẨN NGƯỠNG)
- PHẦN 2: PHA THI THÍCH ỨNG & CHẨN ĐOÁN ONLINE (THỜI GIAN THỰC TRÊN APP - CHỈ NCD VẬN HÀNH)
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
DOCX_OUT_ROOT = ROOT.parent / 'BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx'
DOCX_OUT_BACKEND = ROOT / 'BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx'
DOCX_FINAL_ROOT = ROOT.parent / 'BaoCao_PCAT_NCD_GetGoals_Final.docx'
DOCX_FINAL_BACKEND = ROOT / 'BaoCao_PCAT_NCD_GetGoals_Final.docx'
DOCX_RUTGON_ROOT = ROOT.parent / 'BaoCao_HocThuat_PCAT_RutGon.docx'


def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def build_focused_report():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Text helpers
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(17)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x76, 0x6E)

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
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
        p.paragraph_format.space_after = Pt(4)
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
        p.paragraph_format.space_after = Pt(3)
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
    add_subtitle("Mối quan hệ Phối hợp NCD – NSGA-II trong Tối ưu hóa Đề thi và Chẩn đoán Năng lực Thích ứng (GetGoals TOEIC)")

    # Metadata Table
    t_meta = doc.add_table(rows=1, cols=4)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [("Mô hình AI:", " NCD (Neural CDM)"),
                 ("Thuật toán Tổ hợp:", " NSGA-II & Pruning"),
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
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # TỔNG QUAN VỀ QUAN HỆ "AI CHẠY TRƯỚC - AI CHẠY SAU"
    add_h2("TỔNG QUAN: BẢN CHẤT MỐI QUAN HỆ 'AI CHẠY TRƯỚC - AI CHẠY SAU' GIỮA NCD VÀ NSGA-II")
    add_callout(
        "Trong hệ thống GetGoals: NCD là 'Cây thước đo năng lực' (Evaluator), còn NSGA-II là 'Người thợ tìm kiếm bộ đề' (Search Optimizer). "
        "Do đó, NCD bắt buộc phải được huấn luyện (pre-train) TRƯỚC để học toàn bộ thuộc tính câu hỏi. "
        "Sau đó, NSGA-II mới chạy THỨ HAI, liên tục gửi các bộ đề ứng viên sang cho NCD chấm điểm AUC/Coverage để tiến hóa. "
        "Đến khi đưa lên Mobile App cho thí sinh thi thật, NSGA-II đã hoàn thành nhiệm vụ và NGHỈ HOÀN TOÀN; "
        "chỉ còn duy nhất mô hình NCD vận hành trực tuyến trong thời gian thực (< 30ms).",
        bold_title="KẾT LUẬN QUAN TRỌNG: "
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
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run("Hình 1: Hai pha vận hành cốt lõi của hệ thống PCAT-NCD trong GetGoals (Pha 1 Offline & Pha 2 Online)")
        r_cap.font.name = 'Times New Roman'
        r_cap.font.italic = True
        r_cap.font.size = Pt(9)
        r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # =========================================================================
    # PHẦN 1: PHA TỐI ƯU HÓA OFFLINE
    # =========================================================================
    add_h1("PHẦN 1: PHA TỐI ƯU HÓA OFFLINE (NCD TRAIN TRƯỚC LÀM GIÁM KHẢO ⟷ NSGA-II TỔ HỢP ĐỀ 30 CÂU & HIỆU CHUẨN NGƯỠNG)")
    add_p("Pha Offline được thực thi hoàn toàn trước khi phát hành ứng dụng, gồm 4 mắt xích liên hoàn:")

    add_h2("1.1. Bước 1: Huấn luyện Mô hình NCD Trước (NCD Pre-training)")
    add_p("Bản chất & Mục tiêu: Muốn đánh giá một câu hỏi là Khó hay Dễ, phân loại giỏi/kém thế nào, hệ thống phải học từ dữ liệu. NCD chạy đầu tiên trên tập dữ liệu chuẩn Dense EdNet TOEIC (90 câu hỏi, ma trận Q-matrix K=24 kỹ năng, hàng trăm nghìn tương tác học sinh).", bold_pre="Vai trò: ")
    add_bullet("Ma trận Q-matrix (90 câu x 24 kỹ năng); Lịch sử làm bài TotalData.csv của tập học sinh huấn luyện.", "Input: ")
    add_bullet("File checkpoint đã học xong toàn bộ tham số: model_Dense_EdNetTOEIC_Balanced90_90d_seed20_train_ncd.pt.", "Output: ")
    add_bullet("Vector độ khó câu hỏi d_j ∈ R^24; Vector độ phân biệt k_j; Trọng số mạng PredictNet W_1, W_2 ≥ 0 (ràng buộc đơn điệu Monotonicity); Biases b_1, b_2.", "Bộ tham số học được: ")
    
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

    add_h2("1.2. Bước 2: Cắt tỉa Không gian Ràng buộc Sư phạm (Heuristic Pruning)")
    add_p("Bản chất & Mục tiêu: Nếu chọn ngẫu nhiên 30 câu từ 90 câu ngân hàng, ta có C(90, 30) ≈ 4.1 × 10^23 tổ hợp. Thuật toán Cắt tỉa áp dụng 4 luật sư phạm TOEIC để lọc sạch các bộ đề dị tật trước khi chuyển cho NSGA-II:", bold_pre="Vai trò: ")
    add_bullet("Bắt buộc cả 2 nhánh Dễ và Khó khi kết hợp với Stage 1 đều phủ trọn vẹn 7 Part: 𝒫(S_1 ∪ S_2A) = 𝒫(S_1 ∪ S_2B) = {1..7}.", "1. Ràng buộc Bao phủ 7 Part: ")
    add_bullet("Mỗi stage 10 câu có đúng 5 câu Nghe và 5 câu Đọc: |S_i ∩ Listening| = 5, |S_i ∩ Reading| = 5 (∀ i ∈ {1, 2A, 2B}).", "2. Cân bằng Nghe - Đọc: ")
    add_bullet("Độ khó trung bình bảo đảm: d(S_2A) = -0.032 < d(S_1) = 0.000 < d(S_2B) = +0.185.", "3. Phân tầng Độ khó Thích ứng: ")
    add_bullet("Bảo toàn 100% ngữ cảnh đoạn văn Part 6, 7 và audio Part 3, 4, tuyệt đối không xé lẻ chùm câu hỏi.", "4. Bảo toàn Chùm câu hỏi (Bundle Integrity): ")
    add_p("Kết quả: Rút gọn không gian tìm kiếm xuống đúng 1.440 cấu hình hợp lệ, thời gian tối ưu hóa giảm từ 2.4 giờ xuống còn 26 giây.", bold_pre="Hiệu năng: ")

    add_h2("1.3. Bước 3: Thuật toán NSGA-II Chạy Sau Tổ hợp Bộ đề (NCD làm Giám khảo Chấm điểm)")
    add_p("Bản chất & Mục tiêu: NSGA-II sinh ra các cá thể đề thi x = [S_1, S_2A, S_2B] ∈ ℕ^30. Nhưng làm sao NSGA-II biết cá thể nào tốt? Nó liên tục gọi mô hình NCD (đã train ở Bước 1) làm Giám khảo chấm điểm AUC qua hàm evaluate().", bold_pre="Cơ chế phối hợp: ")
    add_bullet("Quần thể N = 80 cá thể; Tiến hóa qua G = 100 thế hệ; Xác suất lai ghép p_c = 0.9, đột biến p_m = 0.1.", "Tham số NSGA-II: ")
    
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
    add_p("Kết quả hội tụ Pareto: Chọn ra bộ đề tối ưu 30 câu (Seed 20) đạt AUC = 0.7190, ACC = 0.6778, Coverage = 89.48% (lưu vào file optimized_7part_paper_seed20.json).")

    add_h2("1.4. Bước 4: Hiệu chuẩn Ngưỡng Trung vị Phân chặng (Offline Median Calibration)")
    add_p("Bản chất & Mục tiêu: Tránh việc đặt ngưỡng định tuyến cảm tính. Thuật toán lấy 242 học sinh tập train EdNet mô phỏng làm 10 câu Stage 1:", bold_pre="Vai trò: ")
    add_bullet("Khởi tạo e_s = 0 cho từng học sinh, cho NCD chạy 10 epoch Adam để cập nhật e_s.", "Bước 1: ")
    add_bullet("Tính điểm trung bình độ thuần thục trên Stage 1: Mastery(s, S_1) = (1/|C_S1|) * ∑ α_sk. Thu được 242 điểm số.", "Bước 2: ")
    add_bullet("Sắp xếp 242 điểm tăng dần. Lấy trung vị tại vị trí thứ 121 và 122: τ_median = (0.529362 + 0.529427) / 2 = 0.529395 (~0.5294).", "Bước 3: ")
    add_p("Ý nghĩa: Ngưỡng τ_median = 0.5294 chia đều quần thể học sinh chuẩn mực thành đúng 50% Easy và 50% Hard.")

    # =========================================================================
    # PHẦN 2: PHA THI THÍCH ỨNG & CHẨN ĐOÁN ONLINE
    # =========================================================================
    add_h1("PHẦN 2: PHA THI THÍCH ỨNG & CHẨN ĐOÁN ONLINE (THỜI GIAN THỰC TRÊN MOBILE APP - CHỈ NCD VẬN HÀNH)")
    add_p("Khi người dùng mở ứng dụng GetGoals để thi: Bộ đề 30 câu đã chốt cố định, thuật toán NSGA-II đã hoàn thành nhiệm vụ và NGHỈ HOÀN TOÀN. Toàn bộ tiến trình chỉ do mô hình NCD vận hành trực tuyến trong thời gian thực:")

    add_h2("2.1. Giai đoạn 1: Thí sinh làm Đề Cơ sở (Stage 1 - 10 câu Medium)")
    add_p("Thí sinh bắt đầu với 10 câu Medium có độ khó trung bình d = -0.0002 (gồm 5 câu Nghe Part 1, 2, 3 và 5 câu Đọc Part 5, 6).")
    add_p("Khi thí sinh bấm nộp bài 10 câu: NCD Online Optimizer khởi tạo e_s = 0 (tương đương Prior = 50%), chạy 10 epoch Adam trên hàm mất mát BCE Loss để cập nhật vector e_s trong thời gian cực nhanh (< 30ms).")

    add_p("Công thức Tính Điểm Năng lực Trung bình Stage 1:")
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

    add_h2("2.2. Giai đoạn 2: Quyết định Định tuyến Thích ứng Tức thì (< 1ms)")
    add_p("Hệ thống đối chiếu điểm Mastery(s, S_1) với ngưỡng trung vị hiệu chuẩn τ_median = 0.5294:")
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

    add_h2("2.3. Giai đoạn 3: Thí sinh làm Đề Phân nhánh (Stage 2 - 10 câu Easy / Hard)")
    add_bullet("Nếu vào Chặng 2A (Easy, d = -0.032): Làm 10 câu cơ bản gồm Part 2 (2 câu), Part 4 (3 câu) và Part 7 (chùm bài đọc cơ bản 5 câu q76-80). Giúp người học mới bắt đầu không bị áp lực.", "Nhánh Dễ: ")
    add_bullet("Nếu vào Chặng 2B (Hard, d = +0.185): Làm 10 câu nâng cao gồm Part 2 (2 câu), Part 4 (3 câu), Part 5 (1 câu) và Part 7 (chùm bài đọc nâng cao 4 câu q81-84). Giúp phân loại rõ rệt học sinh giỏi.", "Nhánh Khó: ")
    add_p("Cả hai nhánh đều bổ sung hoàn tất Part 4 và Part 7, bảo đảm người học làm đúng 20 câu là hoàn thành 100% cả 7 Part TOEIC.")

    add_h2("2.4. Giai đoạn 4: Báo cáo Chẩn đoán Tri thức Đa chiều 3 Lớp")
    add_p("Khi thí sinh nộp đủ 20 câu: NCD đóng băng trọng số đề thi, tinh chỉnh vector e_s trên toàn bộ 20 câu và giải mã thành Báo cáo 3 lớp:")
    add_bullet("Lớp 1: Bảng điểm 7 Part TOEIC (0 - 100%): Khắc phục triệt để lỗi bị khuyết điểm N/A của bài báo gốc KDD 2025.")
    add_bullet("Lớp 2: Biểu đồ Radar 24 Kỹ năng NCD: Điểm số của từng kỹ năng được tính bằng ánh xạ Score(k) = Sigmoid(e_sk) * 100%.")
    add_bullet("Lớp 3: Top 3 Điểm mạnh (Score >= 65% trên ít nhất 3 câu) và Top 3 Điểm yếu (Score < 60% trên ít nhất 3 câu).")

    add_callout(
        "Giải thích vì sao làm đúng 4/4 Part 7 chỉ đạt 62.3% mà không phải 100%:\n"
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
        ("BaoCao_PCAT_NCD_2Pha_CotLoi.docx (Root)", ROOT.parent / 'BaoCao_PCAT_NCD_2Pha_CotLoi.docx'),
        ("BaoCao_PCAT_NCD_2Pha_CotLoi.docx (Backend)", ROOT / 'BaoCao_PCAT_NCD_2Pha_CotLoi.docx'),
        ("BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx (Root)", DOCX_OUT_ROOT),
        ("BaoCao_ToanDien_ThuatToan_Va_LuongChay_PCAT_NCD.docx (Backend)", DOCX_OUT_BACKEND),
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
