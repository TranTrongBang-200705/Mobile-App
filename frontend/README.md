# Giao Dien Flutter - He Thong GetGoals TOEIC

Ung dung Flutter Frontend doc lap (Standalone UI) duoc xay dung dua tren toan bo chuc nang hien co cua he thong GetGoals TOEIC.

- **Khong can backend phuc tap**: Su dung du lieu gia lap (Mock Data) va State noi bo truc quan.
- **Tat ca cac nut bam su kien deu hoat dong**: Bam chon dap an, kiem tra dung/sai, lat the flashcard, dem nguoc gio thi, nop bai tinh diem, chat hoi dap AI, chuyen doi dark mode, v.v.
- **Thuan Widget co san cua Flutter**: Su dung Material Design 3 chuan, khong bi xung dot thu vien ben thu 3.
- **Ten Ham hoan toan bang Tieng Viet**: De doc, de hieu va de tuy bien.

---

## 1. Cau Truc Thu Muc & Cac Man Hinh

Thu muc ma nguon nam tai `frontend/lib/`:

| File | Man hinh | Chuc nang chinh |
| :--- | :--- | :--- |
| `main.dart` | Khởi chạy app | Cau hinh MaterialApp, Theme, mau sac chu dao |
| `man_hinh/dang_nhap.dart` | Dang nhap & Dang ky | Chuyen tab dang nhap/dang ky, quen mat khau, trai nghiem khach |
| `man_hinh/kiem_tra_dau_vao.dart` | Test dau vao TOEIC | Bai kiem tra phan loai 15p (10 cau Listening & Reading), tinh diem 990 va xep lop lo trinh |
| `man_hinh/trang_chu.dart` | Dashboard & Dieu huong | Streak ngay hoc, thong so tong quan, luoi 8 chuc nang, nhiem vu ngay |
| `man_hinh/luyen_tap.dart` | Luyen tap Part 1 - 7 | Chon part, lam cau hoi A/B/C/D, kiem tra ket qua, xem loi giai chi tiet |
| `man_hinh/thi_thu.dart` | Phong thi thu TOEIC | Danh sach de ETS 2024, dong ho dem nguoc, luoi 20 cau, danh dau flag, nop bai va tinh diem |
| `man_hinh/tu_vung_lat_the.dart` | Flashcard lat the tu vung | Chon chu de (Business, Travel,...), cham lat mat the, danh dau da thuoc / chua thuoc |
| `man_hinh/luyen_doc_va_dich.dart` | Doc tieng Anh & AI | Tab luyen doc co am thanh audio va tra tu nhanh; Tab dich thuat AI thong minh |
| `man_hinh/lo_trinh_hoc.dart` | Lo trinh hoc ca nhan | Theo doi 3 chang muc tieu (450 -> 650 -> 800+), doi muc tieu diem |
| `man_hinh/tro_ly_ai.dart` | Tro ly gia su AI | Khung chat truc quan, chip goi y meo thi, AI tra loi tu dong |
| `man_hinh/so_tay_on_tap.dart` | So tay cau sai | Loc cau sai theo Part, xem lai giai thich, nut lam lai cau sai |
| `man_hinh/tien_do_va_cai_dat.dart` | Tien do & Cai dat | Bieu do thong so hoc tap, bat/tat dark mode, nhac nho hoc, dang xuat |

---

## 2. Bang Ten Cac Ham Tieng Viet

Moi su kien nut bam deu duoc dat ten bang Tieng Viet ro rang:

- **Man hinh Dang Nhap (`dang_nhap.dart`):**
  - `xuLyDangNhap()`: Kiem tra tai khoan va chuyen den Trang chu.
  - `xuLyDangKy()`: Dang ky tai khoan moi.
  - `xuLyQuenMatKhau()`: Mo hop thoai lay lai mat khau qua email.
  - `chuyenDoiCheDo()`: Chuyen qua lai giua form Dang nhap va Dang ky.
  - `dangNhapNhanhKhach()`: Vao thang trang chu khong can dang nhap.

- **Man hinh Test Dau Vao (`kiem_tra_dau_vao.dart`):**
  - `batDauLamTest()`: Khoi dong bai kiem tra 10 cau va bo dem thoi gian 15 phut.
  - `chonDapAn()`: Chon dap an A, B, C, D cho tung cau hoi.
  - `chuyenCauTiepTheo()` / `quayLaiCauTruoc()`: Dieu huong giua cac cau.
  - `xacNhanNopBai()`: Hop thoai xac nhan truoc khi cham diem.
  - `tinhDiemVaPhanLoai()`: Tinh diem Listening, Reading va xep lop (Beginner, Intermediate, Advanced).
  - `batDauLoTrinhDeXuat()`: Chuyen sang hoc theo dung lo trinh he thong goi y.
  - `lamLaiTest()`: Lam lai bai test tu dau.

- **Man hinh Trang Chu (`trang_chu.dart`):**
  - `chuyenTab()`: Chuyen giua cac man hinh qua BottomNavigationBar.
  - `diemDanhHangNgay()`: Nhan streak tang so ngay hoc lien tiep.
  - `hoanThanhNhiemVu()`: Tich hoan thanh checklist nhiem vu hang ngay.
  - `moHopThoaiThongBao()`: Xem thong bao he thong.

- **Man hinh Luyen Tap (`luyen_tap.dart`):**
  - `chonPartLuyenTap()`: Chuyen doi qua lai giua Part 1 den Part 7.
  - `chonDapAn()`: Chon dap an A, B, C, hoac D.
  - `kiemTraDapAn()`: Cham diem va hien thi loi giai thich chi tiet.
  - `chuyenCauTiepTheo()` / `chuyenCauTruoc()`: Dieu huong cau hoi.
  - `luuVaoSoTay()`: Them cau hoi vao so tay on tap.
  - `lamLaiCauHoi()`: Xoa lua chon de lam lai cau hoi.

- **Man hinh Thi Thu (`thi_thu.dart`):**
  - `batDauThiThu()`: Vao phong thi va khoi dong dong ho dem nguoc.
  - `tamDungHoacTiepTuc()`: Tam dung thoi gian lam bai.
  - `chonCauHoi()`: Nhay nhanh den cau bat ky trong danh sach 20 cau.
  - `danhDauXemLai()`: Dat co (Flag) chu y cho cau hoi phan van.
  - `xacNhanNopBai()`: Hop thoai xac nhan truoc khi cham diem.
  - `hienKetQuaThi()`: Tinh diem thang 990 (Listening & Reading) va hien thi popup ket qua.

- **Man hinh Lat The Tu Vung (`tu_vung_lat_the.dart`):**
  - `latTheTuVung()`: Chuyen doi giua Mat truoc (tieng Anh) va Mat sau (nghia Viet).
  - `danhDauDaThuoc()`: Ghi nhan tu da thuoc.
  - `danhDauChuaThuoc()`: Ghi nhan tu can on lai.
  - `xaoTronDanhSach()`: Xao tron ngau nhien thu tu cac the.
  - `doiChuDeTuVung()`: Loc tu vung theo linh vuc (Business, Du lich, v.v.).

- **Man hinh Doc & Dich AI (`luyen_doc_va_dich.dart`):**
  - `chuyenTrangThaiPhatAm()`: Bat/tat phat audio giong doc ban xu.
  - `traCuuTuNhanh()`: Mo hop thoai tra nghia nhanh cho tu duoc bam.
  - `xuLyDichThuat()`: Dich doan van qua AI sang tieng Viet/tieng Anh.
  - `doiChieuDich()`: Chuyen huong dich Viet-Anh hoac Anh-Viet.

- **Man hinh Tro Ly AI (`tro_ly_ai.dart`):**
  - `guiTinNhan()`: Gui thac mac toi tro ly AI.
  - `phanHoiTuDongAI()`: AI tu dong phan tich va tra loi meo thi TOEIC.
  - `chonGoiYCoSan()`: Nhan nhanh cac cau hoi mau de hoi AI.
  - `xoaLichSuTroChuyen()`: Lam moi cuoc tro chuyen.

- **Man hinh Cai Dat (`tien_do_va_cai_dat.dart`):**
  - `chuyenDoiCheDoToi()`: Bat/tat Dark Mode.
  - `chuyenTrangThaiNhacNho()` & `chonGioNhacNho()`: Hen gio hoc hang ngay.
  - `chuyenTrangThaiAmThanh()`: Bat/tat am thanh.
  - `xuLyDangXuat()`: Dang xuat va tro ve man hinh dang nhap.

---

## 3. Huong Dan Chay Ung Dung

De chay thu ung dung Flutter tren may cua ban:

```bash
# Di chuyen vao thu muc frontend
cd frontend

# Lay cac goi phu thuoc Flutter
flutter pub get

# Chay ung dung tren Trinh duyet Chrome (hoac Thiet bi gia lap Android/iOS, Windows desktop)
flutter run -d chrome
# Hoac neu muon chay tren ung dung Windows:
flutter run -d windows
```
