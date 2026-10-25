# GetGoals TOEIC - Mobile App & PCAT AI Adaptive Engine

Ứng dụng luyện thi và kiểm tra trình độ TOEIC thông minh kết hợp hệ thống kiểm tra thích ứng trên máy tính (**PCAT - Personalized Computerized Adaptive Testing**) và mô hình chẩn đoán nhận thức nơ-ron (**NCD - Neural Cognitive Diagnosis**).

---

## 🏛️ Kiến trúc hệ thống (Architecture)

```
├── frontend/                  # Ứng dụng Flutter (Web & Mobile)
│   ├── lib/
│   │   ├── man_hinh/         # Màn hình chức năng (Đăng nhập, Trang chủ, Kiểm tra đầu vào, v.v.)
│   │   └── main.dart         # Entrypoint của Flutter
│   ├── test/                 # Kiểm thử widget & luồng thi thích ứng
│   └── pubspec.yaml          # Quản lý thư viện Flutter
│
├── pcat/                      # Máy chủ AI Backend (FastAPI + PyTorch)
│   ├── pcat_server.py        # API Server phục vụ thi thích ứng & chẩn đoán
│   ├── pcat_live_questions.json  # Ngân hàng 90 câu hỏi TOEIC chuẩn hóa 7 Parts
│   ├── audio_cache/          # Nguồn âm thanh bản xứ cho Part 1-4 Listening
│   ├── image_cache/          # Hình ảnh trực quan cho Part 1 Photographs
│   ├── model/                # Mô hình Neural Cognitive Diagnosis (NCD)
│   ├── dataset/              # Xử lý ma trận Q và dữ liệu thích ứng
│   ├── strategy/             # Thuật toán định tuyến chặng (Routing Strategy)
│   ├── requirements.txt      # Thư viện Python phụ thuộc
│   ├── start_server.bat      # Script khởi chạy Backend nhanh (Windows)
│   └── start_server.ps1      # Script PowerShell khởi chạy Backend
│
└── .gitignore                 # Cấu hình bỏ qua file rác, cache, build
```

---

## 🚀 Tính năng nổi bật

### 1. 📱 Frontend (Flutter)
- **Thi thích ứng 2 chặng (45 phút)**:
  - **Chặng 1**: 10 câu Medium (5 Listening + 5 Reading) khảo sát đa chiều.
  - **Chặng 2**: Tự động rẽ nhánh sang đề Easy hoặc Hard dựa trên năng lực tức thời của thí sinh.
- **Thanh điều hướng câu hỏi trực quan**: Cho phép chuyển nhanh giữa `Câu 1`, `Câu 2`, ..., hiển thị trạng thái hoàn thành từng câu.
- **Đoạn văn đọc hiểu & Trình phát Audio**:
  - Giao diện bài đọc font chữ lớn, nền trắng rõ ràng.
  - Tích hợp phát audio nghe TOEIC bản xứ chuẩn Mỹ/Anh.
- **Hồ sơ năng lực Radar (NCD Spider Chart)**:
  - Xuất phân tích trực quan điểm mạnh, điểm yếu trên 24 kỹ năng và từng Part TOEIC.
- **Giao diện người dùng thuần Việt 100%**: Chuẩn hóa ngôn ngữ, mượt mà và thân thiện.

### 2. 🧠 AI Backend (PCAT + NCD)
- **Engine**: Xây dựng trên nền tảng FastAPI + PyTorch.
- **Định tuyến thích ứng**: Tự động tính toán điểm năng lực tổng hợp và rẽ nhánh thông minh.
- **Chẩn đoán nhận thức NCD**: Đo lường mức độ thuần thục của học viên trên từng khái niệm kiến thức ngữ pháp/từ vựng/kỹ năng nghe.

---

## 🛠️ Hướng dẫn cài đặt & Chạy cục bộ

### 1. Khởi chạy Backend PCAT
```bash
cd pcat
# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy server FastAPI (cổng 8000)
python pcat_server.py
# hoặc chạy file: start_server.bat
```
Server sẽ chạy tại: `http://127.0.0.1:8000` (Tài liệu API Swagger tại `/docs`).

### 2. Khởi chạy Frontend Flutter
```bash
cd frontend
# Cài đặt packages Flutter
flutter pub get

# Chạy trên trình duyệt Web (Port 5000)
flutter run -d chrome --web-port 5000
# hoặc chạy trên thiết bị di động / máy ảo
flutter run
```

---

## 📝 Bản quyền & Giấy phép
Dự án được xây dựng phục vụ mục đích học tập, nghiên cứu và phát triển giải pháp EdTech cá nhân hóa.
