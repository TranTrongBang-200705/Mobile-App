import 'package:flutter/material.dart';
import 'dang_nhap.dart';

/// MAN HINH: TienDoVaCaiDatManHinh
/// Ke thua StatefulWidget vi can quan ly cac trang thai cai dat tuy chon he thong:
/// - batCheDoToi: Cong tac bat tat che do toi (Dark Mode)
/// - batNhacNhoHocTap & gioNhacNho: Cong tac va thoi gian thong bao hoc tap
/// - batAmThanhHieuUng: Cong tac am thanh khi lam bai
class TienDoVaCaiDatManHinh extends StatefulWidget {
  const TienDoVaCaiDatManHinh({super.key});

  @override
  State<TienDoVaCaiDatManHinh> createState() => _TienDoVaCaiDatManHinhState();
}

class _TienDoVaCaiDatManHinhState extends State<TienDoVaCaiDatManHinh> {
  // BIEN TRANG THAI (STATE):
  bool batCheDoToi = false;
  bool batNhacNhoHocTap = true;
  bool batAmThanhHieuUng = true;
  String gioNhacNho = '20:00';

  /// HAM XU LY: chuyenDoiCheDoToi()
  /// Hoat dong: Cap nhat trang thai bat/tat Dark Mode va phan hoi bang SnackBar.
  void chuyenDoiCheDoToi(bool giaTri) {
    setState(() {
      batCheDoToi = giaTri;
    });
    hienThongBao(batCheDoToi ? 'Da bat giao dien toi.' : 'Da chuyen ve giao dien sang.');
  }

  /// HAM XU LY: chuyenTrangThaiNhacNho()
  void chuyenTrangThaiNhacNho(bool giaTri) {
    setState(() {
      batNhacNhoHocTap = giaTri;
    });
    hienThongBao(batNhacNhoHocTap ? 'Da bat nhac nho hoc tap luc $gioNhacNho moi ngay.' : 'Da tat nhac nho.');
  }

  /// HAM XU LY: chonGioNhacNho()
  /// WIDGET: showTimePicker
  /// Hoat dong: Mo hop thoai chon gio chuan Material Design cua he dieu hanh de nguoi dung chon gio/phut.
  Future<void> chonGioNhacNho() async {
    final TimeOfDay? gioDuocChon = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 20, minute: 0),
    );
    if (gioDuocChon != null) {
      setState(() {
        gioNhacNho = '${gioDuocChon.hour.toString().padLeft(2, '0')}:${gioDuocChon.minute.toString().padLeft(2, '0')}';
      });
      hienThongBao('Da dat gio nhac nho hoc tap luc: $gioNhacNho');
    }
  }

  /// HAM XU LY: chuyenTrangThaiAmThanh()
  void chuyenTrangThaiAmThanh(bool giaTri) {
    setState(() {
      batAmThanhHieuUng = giaTri;
    });
    hienThongBao(batAmThanhHieuUng ? 'Da bat am thanh hieu ung khi chon dap an.' : 'Da tat am thanh.');
  }

  /// HAM XU LY: moHopThoaiDoiMatKhau()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Mo hop thoai nhap mat khau cu va mat khau moi.
  void moHopThoaiDoiMatKhau() {
    final TextEditingController matKhauCuController = TextEditingController();
    final TextEditingController matKhauMoiController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Doi mat khau tai khoan'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: matKhauCuController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Mat khau cu',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: matKhauMoiController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Mat khau moi',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Huy'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              hienThongBao('Doi mat khau thanh cong!');
            },
            child: const Text('Xac nhan doi'),
          ),
        ],
      ),
    );
  }

  /// HAM XU LY: xuLyDangXuat()
  /// CO CHE: Navigator.pushAndRemoveUntil
  /// Hoat dong: Xoa sach tat ca cac man hinh dang ton tai trong ngan xep lich su (Stack)
  /// va dieu huong hoc vien quay ve man hinh Dang nhap.
  void xuLyDangXuat() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Xac nhan dang xuat'),
        content: const Text('Ban co chac chan muon dang xuat khoi tai khoan nay?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('O lai'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () {
              Navigator.pop(context);
              hienThongBao('Da dang xuat thanh cong!');
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const DangNhapManHinh()),
                (route) => false, // Xoa toan bo lich su Stack
              );
            },
            child: const Text('Dang xuat', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  /// HAM TIEN ICH: hienThongBao()
  void hienThongBao(String noiDung) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(noiDung),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // WIDGET: Scaffold
    return Scaffold(
      // WIDGET: SingleChildScrollView
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ==================== KHU VUC 1: THE THONG TIN TAI KHOAN ====================
            // WIDGET: Card
            // The Card chua anh dai dien, ten hoc vien, email va hang thanh vien Premium
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: const Padding(
                padding: EdgeInsets.all(16),
                child: Row(
                  children: [
                    // WIDGET: CircleAvatar
                    // Anh dai dien tron voi mau nen blueAccent
                    CircleAvatar(
                      radius: 32,
                      backgroundColor: Colors.blueAccent,
                      child: Icon(Icons.person, size: 36, color: Colors.white),
                    ),
                    SizedBox(width: 16),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Nguyen Van Hoc Vien',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 4),
                        Text('Email: hocvien@getgoals.edu.vn', style: TextStyle(color: Colors.grey, fontSize: 13)),
                        SizedBox(height: 2),
                        Text('Goi: Premium Member', style: TextStyle(color: Colors.green, fontWeight: FontWeight.w600, fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // ==================== KHU VUC 2: THONG KE TIEN DO HOC TAP ====================
            const Text(
              'Thong ke tien do hoc tap',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // Hang 1: Tong gio hoc & Ty le chinh xac
            Row(
              children: [
                Expanded(
                  child: _xayDungTheThongSo(
                    tieuDe: 'Tong gio hoc',
                    giaTri: '28.5 gio',
                    bieuTuong: Icons.access_time,
                    mauSac: Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _xayDungTheThongSo(
                    tieuDe: 'Ty le chinh xac',
                    giaTri: '76%',
                    bieuTuong: Icons.pie_chart_outline,
                    mauSac: Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Hang 2: So de da thi & Streak cao nhat
            Row(
              children: [
                Expanded(
                  child: _xayDungTheThongSo(
                    tieuDe: 'So de da thi',
                    giaTri: '6 de thi',
                    bieuTuong: Icons.assignment_turned_in,
                    mauSac: Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _xayDungTheThongSo(
                    tieuDe: 'Streak cao nhat',
                    giaTri: '14 ngay',
                    bieuTuong: Icons.local_fire_department,
                    mauSac: Colors.deepOrange,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // ==================== KHU VUC 3: CAI DAT HE THONG ====================
            const Text(
              'Cai dat he thong',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Column(
                children: [
                  // WIDGET: SwitchListTile (Che do toi)
                  // Vai tro: Ket hop san ListTile voi cong tac Switch gạt qua lai bat/tat Dark Mode
                  SwitchListTile(
                    title: const Text('Giao dien toi (Dark Mode)'),
                    subtitle: const Text('Giam moi mat khi luyen de ban dem'),
                    secondary: const Icon(Icons.dark_mode_outlined),
                    value: batCheDoToi,
                    onChanged: chuyenDoiCheDoToi,
                  ),
                  const Divider(height: 1),

                  // WIDGET: SwitchListTile (Nhac nho hoc tap)
                  SwitchListTile(
                    title: const Text('Nhac nho hoc tap'),
                    subtitle: Text('Thong bao hoc hang ngay luc $gioNhacNho'),
                    secondary: const Icon(Icons.notifications_active_outlined),
                    value: batNhacNhoHocTap,
                    onChanged: chuyenTrangThaiNhacNho,
                  ),

                  // ListTile chon gio (chi xuat hien khi batNhacNhoHocTap == true)
                  if (batNhacNhoHocTap)
                    ListTile(
                      leading: const SizedBox(width: 24),
                      title: const Text('Chon gio nhac nho'),
                      trailing: TextButton(
                        onPressed: chonGioNhacNho,
                        child: Text(gioNhacNho, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                    ),
                  const Divider(height: 1),

                  // WIDGET: SwitchListTile (Am thanh hieu ung)
                  SwitchListTile(
                    title: const Text('Am thanh hieu ung'),
                    subtitle: const Text('Tieng chuong khi tra loi dung/sai'),
                    secondary: const Icon(Icons.volume_up_outlined),
                    value: batAmThanhHieuUng,
                    onChanged: chuyenTrangThaiAmThanh,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ==================== KHU VUC 4: CAC NUT HANH DONG TAI KHOAN ====================
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Column(
                children: [
                  // WIDGET: ListTile
                  // Nut doi mat khau
                  ListTile(
                    leading: const Icon(Icons.lock_reset, color: Colors.blueAccent),
                    title: const Text('Doi mat khau'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: moHopThoaiDoiMatKhau,
                  ),
                  const Divider(height: 1),

                  // Nut ho tro & lien he
                  ListTile(
                    leading: const Icon(Icons.help_center_outlined, color: Colors.indigo),
                    title: const Text('Trung tam tro giup & Lien he'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => hienThongBao('Email ho tro: support@getgoals.edu.vn'),
                  ),
                  const Divider(height: 1),

                  // Nut dang xuat mau do
                  ListTile(
                    leading: const Icon(Icons.logout, color: Colors.redAccent),
                    title: const Text('Dang xuat', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold)),
                    onTap: xuLyDangXuat,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// HELPER WIDGET: _xayDungTheThongSo()
  Widget _xayDungTheThongSo({
    required String tieuDe,
    required String giaTri,
    required IconData bieuTuong,
    required Color mauSac,
  }) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(tieuDe, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                Icon(bieuTuong, size: 20, color: mauSac),
              ],
            ),
            const SizedBox(height: 8),
            Text(giaTri, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: mauSac)),
          ],
        ),
      ),
    );
  }
}
