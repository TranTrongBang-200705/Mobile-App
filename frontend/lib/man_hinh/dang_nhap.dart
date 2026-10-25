import 'package:flutter/material.dart';
import 'trang_chu.dart';
import 'kiem_tra_dau_vao.dart';

/// MAN HINH: DangNhapManHinh
/// Ke thua StatefulWidget vi man hinh co cac du lieu thay doi trang thai dong thoi (State):
/// - Chuyen doi qua lai giua form Dang nhap va Dang ky (laDangNhap)
/// - An hoac hien thi mat khau (anMatKhau)
/// - Luu tru gia tri nguoi dung go vao cac o TextField thong qua TextEditingController
class DangNhapManHinh extends StatefulWidget {
  const DangNhapManHinh({super.key});

  @override
  State<DangNhapManHinh> createState() => _DangNhapManHinhState();
}

class _DangNhapManHinhState extends State<DangNhapManHinh> {
  // BIEN TRANG THAI (STATE):
  // laDangNhap: true nghia la dang o form Dang nhap; false la dang o form Dang ky
  bool laDangNhap = true;

  // anMatKhau: true nghia la che mat khau thanh dau cham tron; false la hien chu ro rang
  bool anMatKhau = true;

  // OBJECT: TextEditingController
  // Vai tro: Thu thap, doc va dieu khien van ban nhap vao cac o TextField.
  final TextEditingController emailController = TextEditingController();
  final TextEditingController matKhauController = TextEditingController();
  final TextEditingController hoTenController = TextEditingController();

  @override
  void dispose() {
    // Giai phong tai nguyen bo nho khi man hinh bi huy (Tranh ro ri bo nho - Memory Leak)
    emailController.dispose();
    matKhauController.dispose();
    hoTenController.dispose();
    super.dispose();
  }

  /// HAM XU LY: xuLyDangNhap()
  /// Hoat dong: Lay chuoi tu o nhap email va mat khau, kiem tra rong.
  /// Neu hop le thi goi SnackBar thong bao va dung Navigator.pushReplacement de chuyen sang Trang chu.
  void xuLyDangNhap() {
    String email = emailController.text.trim();
    String matKhau = matKhauController.text.trim();

    if (email.isEmpty || matKhau.isEmpty) {
      hienThongBao('Vui lòng nhập đầy đủ email và mật khẩu!');
      return;
    }

    hienThongBao('Đăng nhập thành công! Chúc bạn học tốt.');

    // CO CHE DIEU HUONG: Navigator.pushReplacement
    // Hoat dong: Day TrangChuManHinh vao ngan xep (Stack) va xoa bo man hinh Dang nhap hien tai,
    // giup nguoi dung khi bam nut Back tren dien thoai se khong bi quay nguoc lai form dang nhap nua.
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const TrangChuManHinh()),
    );
  }

  /// HAM XU LY: xuLyDangKy()
  /// Hoat dong: Kiem tra cac truong ho ten, email, mat khau va chuyen huong den Trang chu.
  void xuLyDangKy() {
    String hoTen = hoTenController.text.trim();
    String email = emailController.text.trim();
    String matKhau = matKhauController.text.trim();

    if (hoTen.isEmpty || email.isEmpty || matKhau.isEmpty) {
      hienThongBao('Vui lòng nhập đầy đủ thông tin đăng ký!');
      return;
    }

    hienThongBao('Đăng ký thành công! Hãy bắt đầu hành trình TOEIC.');

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const TrangChuManHinh()),
    );
  }

  /// HAM XU LY: xuLyQuenMatKhau()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Hien thi mot popup hop thoai noi len tren giua man hinh, lam mo phan nen ben duoi.
  void xuLyQuenMatKhau() {
    showDialog(
      context: context,
      builder: (context) {
        final TextEditingController emailKhoiPhucController = TextEditingController();
        return AlertDialog(
          title: const Text('Khôi phục mật khẩu'),
          content: Column(
            mainAxisSize: MainAxisSize.min, // Giup Column chi chiem do cao vua du noi dung ben trong
            children: [
              const Text('Nhập email đăng ký để nhận liên kết đặt lại mật khẩu:'),
              const SizedBox(height: 12),
              TextField(
                controller: emailKhoiPhucController,
                decoration: const InputDecoration(
                  labelText: 'Email của bạn',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email_outlined),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context), // Dong popup hop thoai
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // Dong popup
                hienThongBao('Đã gửi liên kết khôi phục đến email của bạn!');
              },
              child: const Text('Gửi xác nhận'),
            ),
          ],
        );
      },
    );
  }

  /// HAM XU LY: chuyenDoiCheDo()
  /// CO CHE: setState()
  /// Hoat dong: Thong bao cho Flutter framework biet du lieu da thay doi de Flutter ve lai (re-render)
  /// phan giao dien tuong ung (chuyen giua nut Dang nhap va nut Dang ky).
  void chuyenDoiCheDo() {
    setState(() {
      laDangNhap = !laDangNhap;
    });
  }

  /// HAM XU LY: dangNhapNhanhKhach()
  /// Hoat dong: Cho phep nguoi dung trai nghiem cac tinh nang ngay ma khong can go tai khoan.
  void dangNhapNhanhKhach() {
    hienThongBao('Đang trải nghiệm với tư cách Khách.');
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const TrangChuManHinh()),
    );
  }

  /// HAM TIEN ICH: hienThongBao()
  /// WIDGET: SnackBar & ScaffoldMessenger
  /// Hoat dong: Tao mot dai thong bao mau xam/den bay len o duoi day man hinh trong 2 giay de phan hoi hanh dong.
  void hienThongBao(String noiDung) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(noiDung),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating, // Dang noi bong ben tren, khong dinh chat vao day
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // WIDGET: Scaffold
    // Vai tro: Khung xuong co ban cua mot man hinh, cung cap nen tang de dat cac widget con nhu AppBar, Body, Drawer.
    return Scaffold(
      // WIDGET: SafeArea
      // Vai tro: Tu dong tinh toan khoang cach dem (padding) de tranh nhung phan khiem khuyet cua thiet bi
      // (nhu tai tho - Notch, camera duc lo tren dien thoai, thanh trang thai Status Bar).
      body: SafeArea(
        // WIDGET: Center
        // Vai tro: Can chinh widget con nam chinh giua khung nhin theo ca chieu ngang va chieu doc.
        child: Center(
          // WIDGET: SingleChildScrollView
          // Vai tro: Cho phep noi dung cuon len xuong duoc.
          // Dac biet quan trong khi co TextField: Khi ban phim ao dien thoai bat len, widget nay giup giao dien
          // khong bi loi tran man hinh (vang vien den vang - Bottom Overflowed by pixels).
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            // WIDGET: Column
            // Vai tro: Xep cac widget con thanh mot cot doc tu tren xuong duoi.
            // crossAxisAlignment: Stretch giup cac phan tu con keo gian full chieu rong man hinh.
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // WIDGET: Icon
                // Vai tro: Hien thi bieu tuong chiec mu hoc sinh dai dien cho he thong giao duc GetGoals.
                const Icon(
                  Icons.school_rounded,
                  size: 72,
                  color: Colors.blueAccent,
                ),
                const SizedBox(height: 12),

                // WIDGET: Text
                // Vai tro: Hien thi van ban tieu de thuong hieu GetGoals TOEIC.
                const Text(
                  'GetGoals TOEIC',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.blueAccent,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  laDangNhap
                      ? 'Chào mừng bạn quay trở lại! Hãy đăng nhập để tiếp tục.'
                      : 'Tạo tài khoản mới để bắt đầu luyện thi TOEIC ngay!',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey[600], fontSize: 14),
                ),
                const SizedBox(height: 32),

                // CO CHE DIEU KIEN TRONG LIST: if (!laDangNhap) ...[...]
                // Hoat dong: Chi khi nguoi dung o trang thai Dang ky thi o nhap Ho ten moi xuat hien tren giao dien.
                if (!laDangNhap) ...[
                  // WIDGET: TextField
                  // Vai tro: O nhap van ban du lieu ho ten cua nguoi dung.
                  TextField(
                    controller: hoTenController,
                    decoration: const InputDecoration(
                      labelText: 'Họ và tên',
                      prefixIcon: Icon(Icons.person_outline),
                      border: OutlineInputBorder(), // Tao khung vien bao quanh o nhap
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // WIDGET: TextField cho Email
                TextField(
                  controller: emailController,
                  keyboardType: TextInputType.emailAddress, // Goi ban phim co phim '@' tren dien thoai
                  decoration: const InputDecoration(
                    labelText: 'Địa chỉ Email',
                    prefixIcon: Icon(Icons.email_outlined),
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),

                // WIDGET: TextField cho Mat khau
                TextField(
                  controller: matKhauController,
                  obscureText: anMatKhau, // An mat khau thanh dau cham tron
                  decoration: InputDecoration(
                    labelText: 'Mật khẩu',
                    prefixIcon: const Icon(Icons.lock_outline),
                    border: const OutlineInputBorder(),
                    // WIDGET: IconButton
                    // Vai tro: Nut icon nam o cuoi o nhap, bam vao de goi setState() lat nguoc gia tri anMatKhau.
                    suffixIcon: IconButton(
                      icon: Icon(anMatKhau ? Icons.visibility_off : Icons.visibility),
                      onPressed: () {
                        setState(() {
                          anMatKhau = !anMatKhau;
                        });
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 8),

                // Nut Quen mat khau (chi hien khi dang o tab Dang nhap)
                if (laDangNhap)
                  Align(
                    alignment: Alignment.centerRight,
                    // WIDGET: TextButton
                    // Vai tro: Nut dang chu khong co nen mau, thich hop cho cac hanh dong phu nhu "Quen mat khau?".
                    child: TextButton(
                      onPressed: xuLyQuenMatKhau,
                      child: const Text('Quên mật khẩu?'),
                    ),
                  ),

                const SizedBox(height: 16),

                // WIDGET: ElevatedButton
                // Vai tro: Nut bam noi chinh co mau nen xanh duong, dung cho hanh dong quan trong nhat tren man hinh.
                ElevatedButton(
                  onPressed: laDangNhap ? xuLyDangNhap : xuLyDangKy,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    laDangNhap ? 'ĐĂNG NHẬP' : 'ĐĂNG KÝ TÀI KHOẢN',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),

                const SizedBox(height: 12),

                // WIDGET: Row
                // Vai tro: Xep cac widget con nam tren cung mot hang ngang.
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(laDangNhap ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'),
                    TextButton(
                      onPressed: chuyenDoiCheDo,
                      child: Text(
                        laDangNhap ? 'Đăng ký ngay' : 'Đăng nhập ngay',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),

                // WIDGET: Divider
                // Vai tro: Duong ke ngang nhe ngan cach giua khu vuc dang nhap va cac tuy chon phu.
                const Divider(height: 32),

                // WIDGET: OutlinedButton.icon
                // Vai tro: Nut bam vien ngoai vien mau xam nhe kem icon la ban, dung cho tinh nang Trai nghiem khach.
                OutlinedButton.icon(
                  onPressed: dangNhapNhanhKhach,
                  icon: const Icon(Icons.explore_outlined),
                  label: const Text('Trải nghiệm nhanh (Khách)'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
                const SizedBox(height: 8),

                // WIDGET: TextButton.icon
                // Vai tro: Nut bam nhanh dan thang toi Bai kiem tra trinh do dau vao de nguoi hoc danh gia nang luc.
                TextButton.icon(
                  onPressed: () {
                    // WIDGET: Navigator.push
                    // Vai tro: Day mot man hinh moi de len man hinh hien tai, cho phep quay lai bang nut Back.
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const KiemTraDauVaoManHinh()),
                    );
                  },
                  icon: const Icon(Icons.psychology_outlined, color: Colors.blueAccent),
                  label: const Text(
                    'Làm bài test đầu vào (Đánh giá trình độ)',
                    style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blueAccent),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
