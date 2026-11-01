import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ArrowStyle
import matplotlib.patheffects as path_effects
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_PATH = ROOT / 'scripts' / 'pcat_ncd_comprehensive_workflow.png'

def create_diagram():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FAFC')

    # Title Banner
    ax.text(8.0, 9.6, "KIẾN TRÚC TOÀN DIỆN HỆ THỐNG PCAT-NCD (GETGOALS TOEIC)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(8.0, 9.25, "Luồng tích hợp giữa Tối ưu đề Đa mục tiêu (NSGA-II) và Chẩn đoán Nơ-ron Thích ứng (NCD)", 
            ha='center', va='center', fontsize=10, style='italic', color='#475569')

    # Helper function for card boxes
    def draw_box(x, y, w, h, title, items, header_bg='#1E3A8A', body_bg='#FFFFFF', border_col='#CBD5E1'):
        # Body
        body = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor=body_bg, edgecolor=border_col, linewidth=1.2, zorder=2)
        ax.add_patch(body)
        # Header banner
        header = FancyBboxPatch((x, y + h - 0.45), w, 0.45, boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor=header_bg, edgecolor=header_bg, linewidth=1, zorder=3)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 0.22, title, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='#FFFFFF', zorder=4)
        # Lines
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

    # ------------------ TOP SECTION: OFFLINE OPTIMIZATION & CALIBRATION ------------------
    # Background region for Offline
    bg_offline = FancyBboxPatch((0.4, 4.8), 15.2, 4.2, boxstyle="round,pad=0.03,rounding_size=0.1",
                                facecolor='#EFF6FF', edgecolor='#BFDBFE', linewidth=1.5, zorder=1)
    ax.add_patch(bg_offline)
    ax.text(0.7, 8.8, "PHA 1 & 2: HUẤN LUYỆN, TỐI ƯU HÓA ĐỀ & HIỆU CHUẨN NGƯỠNG (OFFLINE)", 
            ha='left', va='center', fontsize=10.5, fontweight='bold', color='#1E40AF', zorder=2)

    # Box 1: Ngân hàng 90 câu & 242 học sinh
    draw_box(0.7, 5.2, 3.2, 3.3, "1. DỮ LIỆU ĐẦU VÀO", [
        "• Ngân hàng đề: 90 câu EdNet",
        "  - Part 1: 3 câu | Part 2: 12 câu",
        "  - Part 3: 15 câu | Part 4: 9 câu",
        "  - Part 5: 25 câu | Part 6: 12 câu",
        "  - Part 7: 14 câu",
        "• 242 học sinh huấn luyện",
        "• Q-matrix: 24 kỹ năng (K=24)",
        "• Checkpoint NCD Model (Seed 20)"
    ], header_bg='#3B82F6')

    # Box 2: Cắt tỉa Heuristic
    draw_box(4.3, 5.2, 3.3, 3.3, "2. CẮT TỈA HEURISTIC", [
        "• Mục tiêu: Giảm không gian tìm kiếm",
        "• 4 Ràng buộc Sư phạm TOEIC:",
        "  1. Bao phủ trọn vẹn 7 Part",
        "  2. Cân bằng: 5 Nghe + 5 Đọc",
        "  3. Độ khó: d(2A) < d(1) < d(2B)",
        "  4. Bảo toàn Chùm câu hỏi",
        "• Kết quả: Rút gọn từ hàng tỷ tỷ",
        "  tổ hợp xuống đúng 1.440 cấu hình",
        "• Giảm thời gian: 2.4h -> 26 giây"
    ], header_bg='#0284C7')

    # Box 3: NSGA-II Tối ưu đề
    draw_box(8.0, 5.2, 3.4, 3.3, "3. THUẬT TOÁN NSGA-II", [
        "• Quần thể: N=80 | Thế hệ: G=100",
        "• Nhiễm sắc thể x in N^30 (30 câu)",
        "• Tối ưu đồng thời 3 hàm mục tiêu:",
        "  - max f1(x) = AUC (0.7190)",
        "  - max f2(x) = Coverage (89.48%)",
        "  - min f3(x) = Exposure (Tránh lộ đề)",
        "• Output: Bộ đề tối ưu 30 câu:",
        "  - Stage 1 (10 câu Medium, d=0.00)",
        "  - Stage 2A (10 câu Easy, d=-0.032)",
        "  - Stage 2B (10 câu Hard, d=+0.185)"
    ], header_bg='#4F46E5')

    # Box 4: Hiệu chuẩn Ngưỡng tau_median
    draw_box(11.8, 5.2, 3.5, 3.3, "4. HIỆU CHUẨN NGƯỠNG TỰ ĐỘNG", [
        "• Input: 242 học sinh tập Train",
        "• Chạy mô phỏng 10 câu Stage 1:",
        "  - Khởi tạo e_s = 0",
        "  - NCD cập nhật 10 epoch Adam",
        "  - Tính điểm Mastery trên Stage 1:",
        "    Mastery(s) = (1/|C_S1|) * sum(alpha_sk)",
        "• Thu được 242 điểm số -> Sắp xếp",
        "• Lấy trung vị (Median Split):",
        "  tau_median = 0.529395 (~0.5294)",
        "• Chia đều quần thể 50% Easy / 50% Hard"
    ], header_bg='#7C3AED')

    # Arrows for Top Section
    draw_arrow(3.9, 6.85, 4.3, 6.85, "Lọc 4 Ràng buộc")
    draw_arrow(7.6, 6.85, 8.0, 6.85, "1.440 cấu hình")
    draw_arrow(11.4, 6.85, 11.8, 6.85, "Đề Stage 1")

    # ------------------ BOTTOM SECTION: ONLINE ADAPTIVE TESTING ------------------
    bg_online = FancyBboxPatch((0.4, 0.4), 15.2, 4.1, boxstyle="round,pad=0.03,rounding_size=0.1",
                               facecolor='#F0FDF4', edgecolor='#BBF7D0', linewidth=1.5, zorder=1)
    ax.add_patch(bg_online)
    ax.text(0.7, 4.2, "PHA 3 & 4: THI THÍCH ỨNG TRỰC TUYẾN & CHẨN ĐOÁN TRI THỨC ĐA CHIỀU (ONLINE)", 
            ha='left', va='center', fontsize=10.5, fontweight='bold', color='#166534', zorder=2)

    # Box 5: Thí sinh làm Stage 1
    draw_box(0.7, 0.7, 3.2, 3.2, "BƯỚC 1: THI STAGE 1 (MEDIUM)", [
        "• Thí sinh nhận 10 câu hỏi Medium:",
        "  - 5 câu Listening (Part 1, 2, 3)",
        "  - 5 câu Reading (Part 5, 6)",
        "• Thí sinh nộp 10 câu trả lời",
        "• NCD Online Optimizer:",
        "  - Khởi tạo e_s = 0 (Prior = 50%)",
        "  - 10 epoch Adam (BCE Loss)",
        "• Tính điểm Mastery(s, S1)"
    ], header_bg='#059669')

    # Box 6: Định tuyến NCD
    draw_box(4.3, 0.7, 3.3, 3.2, "BƯỚC 2: ĐỊNH TUYẾN THÍCH ỨNG", [
        "• So sánh Mastery(s, S1) với tau_median:",
        "• Nếu Mastery < 0.5294:",
        "  --> Chuyển sang Stage 2A (Easy)",
        "  --> Đề cơ bản, động viên người học",
        "• Nếu Mastery >= 0.5294:",
        "  --> Chuyển sang Stage 2B (Hard)",
        "  --> Đề nâng cao, phân loại khá giỏi",
        "• Quyết định tức thì trong < 50ms"
    ], header_bg='#0D9488')

    # Box 7: Làm Stage 2
    draw_box(8.0, 0.7, 3.4, 3.2, "BƯỚC 3: THI STAGE 2 (EASY / HARD)", [
        "• Nhánh 2A (Easy - 10 câu):",
        "  - Part 2, Part 4, Part 7 (chùm 5 câu)",
        "• Nhánh 2B (Hard - 10 câu):",
        "  - Part 2, Part 4, Part 5, Part 7 (4 câu)",
        "• Bảo đảm: Tổng 2 Stage = 20 câu",
        "• Phủ 100% trọn vẹn 7 Part TOEIC",
        "• Bổ sung hoàn chỉnh Part 4 và Part 7"
    ], header_bg='#D97706')

    # Box 8: Báo cáo Chẩn đoán 3 Lớp
    draw_box(11.8, 0.7, 3.5, 3.2, "BƯỚC 4: BÁO CÁO CHẨN ĐOÁN 3 LỚP", [
        "• Đóng băng đề, NCD tinh chỉnh e_s:",
        "  alpha_s = Sigmoid(e_s) in [0, 1]^24",
        "• 1. Bảng điểm 7 Part TOEIC (0 - 100%)",
        "  - Ví dụ: Part 7 đúng 4/4 -> 62.3%",
        "• 2. Biểu đồ Radar 24 Kỹ năng EdNet",
        "• 3. Top 3 Điểm mạnh (Score >= 65%)",
        "  & Top 3 Điểm yếu (Score < 60%)",
        "• Gợi ý Lộ trình học thích ứng GetGoals"
    ], header_bg='#DC2626')

    # Bottom arrows
    draw_arrow(3.9, 2.3, 4.3, 2.3, "10 đáp án")
    draw_arrow(7.6, 2.3, 8.0, 2.3, "Phân nhánh")
    draw_arrow(11.4, 2.3, 11.8, 2.3, "Nộp đủ 20 câu")

    # Connect Offline to Online
    draw_arrow(10.0, 5.2, 2.3, 3.9, "Bộ đề 30 câu (Medium / Easy / Hard)", color='#2563EB', rad=0.25)
    draw_arrow(13.5, 5.2, 6.0, 3.9, "Ngưỡng tau_median = 0.5294", color='#7C3AED', rad=0.25)

    plt.tight_layout()
    plt.savefig(IMG_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Flowchart successfully saved to {IMG_PATH}")

if __name__ == '__main__':
    create_diagram()
