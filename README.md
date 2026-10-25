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
  - **Chặng 1**: 10 câu Medium (5 Listening + 5 Reading) khảo sát toàn diện các kỹ năng.
  - **Chặng 2**: Thuật toán AI tự động phân nhánh sang đề Easy hoặc Hard dựa trên kết quả Chặng 1.
- **Thanh điều hướng câu hỏi trực quan**: Cho phép chuyển nhanh giữa `Câu 1`, `Câu 2`, ..., hiển thị tích xanh các câu đã trả lời.
- **Đoạn văn đọc hiểu & Trình phát Audio**:
  - Giao diện bài đọc font chữ lớn, nền trắng rõ ràng.
  - Tích hợp trình phát audio nghe TOEIC bản xứ chuẩn Mỹ/Anh.
- **Hồ sơ năng lực Radar (NCD Spider Chart)**:
  - Xuất phân tích trực quan điểm mạnh, điểm yếu trên 24 kỹ năng và từng Part TOEIC.
- **Giao diện thuần Việt 100%**: Chuẩn hóa ngôn ngữ có dấu đầy đủ, tự nhiên và thân thiện.

### 2. 🧠 AI Backend (PCAT + NCD)
- **Engine**: Xây dựng trên nền tảng FastAPI + PyTorch.
- **Định tuyến thích ứng**: Tự động tính toán điểm năng lực tức thời và rẽ nhánh thông minh.
- **Chẩn đoán nhận thức NCD**: Đo lường mức độ thuần thục của học viên trên từng khái niệm kiến thức ngữ pháp/từ vựng/kỹ năng nghe.

---

## 📋 Yêu cầu môi trường (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:
1. **Git**: [Tải về tại đây](https://git-scm.com/)
2. **Python**: Phiên bản `3.10` trở lên (Khuyến nghị 3.10 - 3.12)
3. **Flutter SDK**: Phiên bản `3.x` trở lên ([Hướng dẫn cài đặt Flutter](https://docs.flutter.dev/get-started/install))
4. **Trình duyệt Web** (Google Chrome / Microsoft Edge) hoặc **Android Studio** (nếu muốn chạy app di động).

---

## 🛠️ Hướng dẫn từng bước khi Clone về máy (Step-by-Step Setup)

### Bước 1: Clone dự án về máy tính
Mở Terminal hoặc Command Prompt / PowerShell và gõ:
```bash
git clone https://github.com/TranTrongBang-200705/Mobile-App.git
cd Mobile-App
```

---

### Bước 2: Thiết lập và Chạy Backend (PCAT AI)

Mở một cửa sổ Terminal thứ nhất:

```bash
# 1. Di chuyển vào thư mục backend PCAT
cd pcat

# 2. Tạo môi trường ảo Python (.venv)
python -m venv .venv

# 3. Kích hoạt môi trường ảo
# Trên Windows (Command Prompt):
.venv\Scripts\activate.bat
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên macOS / Linux:
source .venv/bin/activate

# 4. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 5. Khởi động Backend Server
python pcat_server.py
```
> **Mẹo trên Windows**: Sau khi đã cài thư viện xong một lần, những lần sau bạn chỉ cần nhấp đúp chuột vào file `start_server.bat` để chạy server ngay lập tức!

✅ **Kiểm tra**: Mở trình duyệt truy cập [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Nếu thấy trang Swagger UI hiện ra tức là Backend đã sẵn sàng!

---

### Bước 3: Thiết lập và Chạy Frontend (Flutter App)

Mở một cửa sổ Terminal thứ hai (giữ nguyên cửa sổ Backend đang chạy):

```bash
# 1. Di chuyển vào thư mục frontend
cd frontend

# 2. Tải và cài đặt các package Flutter
flutter pub get

# 3. Chạy ứng dụng trên Trình duyệt Web (Port 5000)
flutter run -d chrome --web-port 5000
```

> **Ghi chú chạy trên các nền tảng khác**:
> - Chạy bằng Microsoft Edge: `flutter run -d edge --web-port 5000`
> - Chạy web server độc lập: `flutter run -d web-server --web-port 5000 --web-hostname 127.0.0.1`
> - Chạy trên thiết bị di động / máy ảo Android: 
>   - Cắm điện thoại bật USB Debugging hoặc bật Android Emulator.
>   - Chạy lệnh `flutter run`.
>   - *(Lưu ý: Nếu chạy trên máy ảo Android, hãy vào `frontend/lib/man_hinh/kiem_tra_dau_vao.dart` đổi `http://127.0.0.1:8000` thành `http://10.0.2.2:8000` để máy ảo kết nối được vào máy tính chủ)*.

---

## 🧪 Chạy kiểm thử tự động (Running Tests)

Để kiểm tra độ ổn định của ứng dụng và logic thích ứng:
```bash
cd frontend
flutter test
```

---

## ❓ Xử lý lỗi thường gặp (Troubleshooting)

1. **Lỗi cổng 8000 hoặc 5000 đang bị chiếm dụng**:
   - Windows PowerShell:
     ```powershell
     Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
     Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
     ```
2. **Không nghe được Audio trên Web**:
   - Trình duyệt Chrome có chính sách chặn tự động phát âm thanh (Autoplay Policy). Hãy bấm trực tiếp nút **Play** trên màn hình để nghe.
3. **Lỗi `ExecutionPolicy` khi kích hoạt Virtualenv trên PowerShell**:
   - Mở PowerShell quyền Administrator và chạy: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.

---

## 📝 Bản quyền & Đóng góp
Dự án được xây dựng phục vụ mục đích học tập, nghiên cứu và phát triển giải pháp EdTech cá nhân hóa. Mọi đóng góp và báo lỗi xin vui lòng tạo Issue trên GitHub!
