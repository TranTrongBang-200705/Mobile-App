import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ArrowStyle
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_PATH = ROOT / 'scripts' / 'pcat_ncd_comprehensive_workflow.png'

def create_diagram():
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Title Banner
    ax.text(8.0, 10.05, "HAI PHA VẬN HÀNH CỐT LÕI CỦA HỆ THỐNG PCAT-NCD (GETGOALS TOEIC)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(8.0, 9.72, "Mối quan hệ 'Ai chạy trước - Ai chạy sau': NCD huấn luyện làm Giám khảo -> NSGA-II tổ hợp đề -> NCD chạy trực tuyến trên App", 
            ha='center', va='center', fontsize=9.8, style='italic', color='#334155')

    def draw_box(x, y, w, h, title, items, header_bg='#1E3A8A', body_bg='#FFFFFF', border_col='#CBD5E1'):
        body = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor=body_bg, edgecolor=border_col, linewidth=1.2, zorder=2)
        ax.add_patch(body)
        header = FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor=header_bg, edgecolor=header_bg, linewidth=1, zorder=3)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 0.22, title, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='#FFFFFF', zorder=4)
        for i, line in enumerate(items):
            ax.text(x + 0.12, y + h - 0.65 - i * 0.23, line, ha='left', va='center',
                    fontsize=7.5, color='#1E293B', zorder=4)

    def draw_arrow(x1, y1, x2, y2, text='', color='#475569', rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.8, 
                                    mutation_scale=14, connectionstyle=connectionstyle),
                    zorder=5)
        if text:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.1, text, ha='center', va='center', fontsize=7.2, fontweight='bold',
                    color=color, bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.8),
                    zorder=6)

    # ------------------ TOP SECTION: PHẦN 1 - OFFLINE OPTIMIZATION ------------------
    bg_offline = FancyBboxPatch((0.4, 5.2), 15.2, 4.3, boxstyle="round,pad=0.03,rounding_size=0.1",
                                facecolor='#EFF6FF', edgecolor='#93C5FD', linewidth=1.8, zorder=1)
    ax.add_patch(bg_offline)
    ax.text(0.7, 9.25, "PHẦN 1: PHA OFFLINE - NCD HUẤN LUYỆN TRƯỚC LÀM GIÁM KHẢO ⟷ NSGA-II TỔ HỢP ĐỀ 30 CÂU & HIỆU CHUẨN", 
            ha='left', va='center', fontsize=10.5, fontweight='bold', color='#1E40AF', zorder=2)

    # Box 1: NCD Huấn luyện trước
    draw_box(0.7, 5.5, 3.2, 3.5, "BƯỚC 1: NCD TRAIN TRƯỚC", [
        "• Mục tiêu: Học tri thức 90 câu hỏi",
        "• Dữ liệu: Dense EdNet TOEIC",
        "• Học ra các tham số câu hỏi:",
        "  - Vector độ khó d_j (24 chiều)",
        "  - Vector độ phân biệt k_j",
        "  - Trọng số tương tác W1, W2 >= 0",
        "• Đóng gói Checkpoint PT:",
        "  model_seed20_train_ncd.pt",
        "--> NCD SẴN SÀNG LÀM GIÁM KHẢO"
    ], header_bg='#2563EB')

    # Box 2: Cắt tỉa Heuristic
    draw_box(4.3, 5.5, 3.3, 3.5, "BƯỚC 2: CẮT TỈA HEURISTIC", [
        "• Mục tiêu: Giảm không gian tìm kiếm",
        "• 4 Ràng buộc Sư phạm TOEIC:",
        "  1. Bao phủ trọn vẹn 7 Part",
        "  2. Cân bằng: 5 Nghe + 5 Đọc",
        "  3. Độ khó: d(2A) < d(1) < d(2B)",
        "  4. Bảo toàn Chùm (Bundle Size)",
        "• Rút gọn C(90, 30) = 4.1x10^23",
        "  xuống đúng 1.440 cấu hình hợp lệ",
        "• Rút ngắn thời gian: 2.4h -> 26 giây"
    ], header_bg='#0284C7')

    # Box 3: NSGA-II Tối ưu đề
    draw_box(8.0, 5.5, 3.4, 3.5, "BƯỚC 3: NSGA-II CHẠY SAU", [
        "• Quần thể: N=80 | 100 thế hệ",
        "• NSGA-II sinh đề x in N^30 (30 câu)",
        "• GỬI SANG NCD CHẤM ĐIỂM (AUC):",
        "  NCD lấy 242 học sinh test thử",
        "  --> trả về AUC = 0.7190",
        "• Tối ưu 3 mục tiêu Pareto:",
        "  max AUC (71.9%), max Cov (89.5%)",
        "• Output: Chốt đề 30 câu tối ưu:",
        "  S1 (Medium), S2A (Easy), S2B (Hard)"
    ], header_bg='#4F46E5')

    # Box 4: Hiệu chuẩn Ngưỡng tau_median
    draw_box(11.8, 5.5, 3.5, 3.5, "BƯỚC 4: HIỆU CHUẨN NGƯỠNG", [
        "• Input: 242 học sinh tập Train",
        "• NCD chạy thử 10 câu Stage 1:",
        "  - Khởi tạo e_s = 0",
        "  - 10 epoch Adam cập nhật e_s",
        "  - Mastery(s) = mean(Sigmoid(e_s))",
        "• Thu được 242 điểm -> Sắp xếp",
        "• Lấy trung vị (Median Split):",
        "  tau_median = 0.529395 (~0.5294)",
        "--> CHIA ĐỀU 50% DỄ / 50% KHÓ"
    ], header_bg='#7C3AED')

    # Arrows for Top Section
    draw_arrow(3.9, 7.25, 4.3, 7.25, "Cung cấp d_j, k_j")
    draw_arrow(7.6, 7.25, 8.0, 7.25, "1.440 cấu hình")
    draw_arrow(11.4, 7.25, 11.8, 7.25, "Đề Stage 1")

    # ------------------ BOTTOM SECTION: PHẦN 2 - ONLINE TESTING ------------------
    bg_online = FancyBboxPatch((0.4, 0.4), 15.2, 4.3, boxstyle="round,pad=0.03,rounding_size=0.1",
                               facecolor='#F0FDF4', edgecolor='#86EFAC', linewidth=1.8, zorder=1)
    ax.add_patch(bg_online)
    ax.text(0.7, 4.45, "PHẦN 2: PHA ONLINE - THI THÍCH ỨNG & CHẨN ĐOÁN TRÊN APP (CHỈ NCD CHẠY, NSGA-II ĐÃ XONG NHIỆM VỤ)", 
            ha='left', va='center', fontsize=10.5, fontweight='bold', color='#166534', zorder=2)

    # Box 5: Thí sinh làm Stage 1
    draw_box(0.7, 0.7, 3.2, 3.5, "GIAI ĐOẠN 1: THI STAGE 1", [
        "• Thí sinh nhận 10 câu Medium:",
        "  - 5 Nghe (P1, P2, P3: chùm b1426)",
        "  - 5 Đọc (P5, P6: chùm b5213)",
        "• NCD Online Optimizer:",
        "  - e_s khởi tạo = 0 (Prior = 50%)",
        "  - 10 epoch Adam tối ưu e_s",
        "  - Chạy tức thì trong < 30ms",
        "• Tính điểm Mastery(s, S1)"
    ], header_bg='#059669')

    # Box 6: Định tuyến NCD
    draw_box(4.3, 0.7, 3.3, 3.5, "GIAI ĐOẠN 2: ĐỊNH TUYẾN NCD", [
        "• So sánh Mastery(s, S1) với tau:",
        "• Nếu Mastery < 0.5294:",
        "  --> Chuyển sang Stage 2A (Easy)",
        "  --> Đề cơ bản, chống nản lòng",
        "• Nếu Mastery >= 0.5294:",
        "  --> Chuyển sang Stage 2B (Hard)",
        "  --> Đề nâng cao, phân loại khá giỏi",
        "• Ra quyết định rẽ nhánh trong < 1ms"
    ], header_bg='#0D9488')

    # Box 7: Làm Stage 2
    draw_box(8.0, 0.7, 3.4, 3.5, "GIAI ĐOẠN 3: THI STAGE 2", [
        "• Nhánh 2A (Easy - 10 câu):",
        "  - P2, P4 (chùm b1810), P7 (chùm b5284)",
        "• Nhánh 2B (Hard - 10 câu):",
        "  - P2, P4 (chùm b2071), P5, P7 (b5322)",
        "• Đảm bảo tổng 2 Stage = 20 câu",
        "• Phủ trọn vẹn 100% cả 7 Part TOEIC",
        "• Bổ sung hoàn chỉnh Part 4 và Part 7"
    ], header_bg='#D97706')

    # Box 8: Báo cáo Chẩn đoán 3 Lớp
    draw_box(11.8, 0.7, 3.5, 3.5, "GIAI ĐOẠN 4: BÁO CÁO 3 LỚP", [
        "• NCD đóng băng đề, tinh chỉnh e_s:",
        "  alpha_s = Sigmoid(e_s) in [0, 1]^24",
        "• 1. Bảng điểm 7 Part (0 - 100%)",
        "  - Ví dụ: Đúng 4/4 Part 7 -> 62.3%",
        "• 2. Biểu đồ Radar 24 Kỹ năng EdNet",
        "• 3. Top 3 Điểm mạnh (Score >= 65%)",
        "  & Top 3 Điểm yếu (Score < 60%)",
        "• Gợi ý Lộ trình học cá nhân hóa"
    ], header_bg='#DC2626')

    # Bottom arrows
    draw_arrow(3.9, 2.45, 4.3, 2.45, "10 đáp án")
    draw_arrow(7.6, 2.45, 8.0, 2.45, "Phân nhánh")
    draw_arrow(11.4, 2.45, 11.8, 2.45, "Nộp đủ 20 câu")

    # Connect Offline to Online
    draw_arrow(10.0, 5.5, 2.3, 4.2, "Bộ đề 30 câu cố định (Medium/Easy/Hard)", color='#2563EB', rad=0.25)
    draw_arrow(13.5, 5.5, 6.0, 4.2, "Ngưỡng hiệu chuẩn tau_median = 0.5294", color='#7C3AED', rad=0.25)

    plt.tight_layout()
    plt.savefig(IMG_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Workflow diagram refreshed: {IMG_PATH}")

if __name__ == '__main__':
    create_diagram()
