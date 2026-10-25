import 'package:flutter/material.dart';
import 'luyen_tap.dart';
import 'thi_thu.dart';
import 'tu_vung_lat_the.dart';
import 'luyen_doc_va_dich.dart';
import 'lo_trinh_hoc.dart';
import 'tro_ly_ai.dart';
import 'so_tay_on_tap.dart';
import 'tien_do_va_cai_dat.dart';
import 'kiem_tra_dau_vao.dart';

/// MAN HINH: TrangChuManHinh
/// Ke thua StatefulWidget vi can quan ly:
/// - Vi tri tab hien tai dang chon tren BottomNavigationBar (viTriTabHienTai)
/// - So ngay hoc lien tiep (soNgayHocLienTiep - Streak)
/// - Trang thai hoan thanh cua danh sach checklist nhiem vu hang ngay (danhSachNhiemVu)
class TrangChuManHinh extends StatefulWidget {
  const TrangChuManHinh({super.key});

  @override
  State<TrangChuManHinh> createState() => _TrangChuManHinhState();
}

class _TrangChuManHinhState extends State<TrangChuManHinh> {
  // BIEN TRANG THAI:
  // viTriTabHienTai: Chi so tab duoi day man hinh (0: Trang chu, 1: Luyen tap, 2: Thi thu, 3: Tu vung, 4: Tai khoan)
  int viTriTabHienTai = 0;

  // Streak: So ngay hoc lien tiep
  int soNgayHocLienTiep = 7;
  bool daDiemDanhHomNay = false;

  // Du lieu nhiem vu hang ngay (Daily Quests)
  List<Map<String, dynamic>> danhSachNhiemVu = [
    {'tieuDe': 'Hoàn thành 10 câu Part 5', 'hoanThanh': true, 'diem': '+20 XP'},
    {'tieuDe': 'Học 15 từ vựng chủ đề Business', 'hoanThanh': false, 'diem': '+15 XP'},
    {'tieuDe': 'Luyện đọc 1 đoạn văn tiếng Anh', 'hoanThanh': false, 'diem': '+10 XP'},
    {'tieuDe': 'Ôn lại 5 câu sai trong sổ tay', 'hoanThanh': false, 'diem': '+10 XP'},
  ];

  /// HAM XU LY: chuyenTab()
  /// Hoat dong: Cap nhat bien viTriTabHienTai va kich hoat setState() de re-render lai Scaffold body
  /// sang tab duoc nguoi dung nhan chon tren BottomNavigationBar.
  void chuyenTab(int viTriMoi) {
    setState(() {
      viTriTabHienTai = viTriMoi;
    });
  }

  /// HAM XU LY: diemDanhHangNgay()
  /// Hoat dong: Tang chuoi streak len 1 ngay va thong bao SnackBar chuc mung.
  void diemDanhHangNgay() {
    if (daDiemDanhHomNay) {
      hienThongBao('Bạn đã điểm danh hôm nay rồi! Hãy duy trì chuỗi ngày nhé.');
      return;
    }
    setState(() {
      daDiemDanhHomNay = true;
      soNgayHocLienTiep += 1;
    });
    hienThongBao('Điểm danh thành công! Chuỗi học của bạn là $soNgayHocLienTiep ngày 🔥');
  }

  /// HAM XU LY: hoanThanhNhiemVu()
  /// Hoat dong: Dao nguoc trang thai true/false cua checkbox nhiem vu hang ngay.
  void hoanThanhNhiemVu(int viTri) {
    setState(() {
      danhSachNhiemVu[viTri]['hoanThanh'] = !danhSachNhiemVu[viTri]['hoanThanh'];
    });
    if (danhSachNhiemVu[viTri]['hoanThanh']) {
      hienThongBao('Chúc mừng! Bạn đã hoàn thành: ${danhSachNhiemVu[viTri]['tieuDe']}');
    }
  }

  /// HAM XU LY: moHopThoaiThongBao()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Hien thi hop thoai thong bao cap nhat he thong khi nguoi dung bam bieu tuong chuong o AppBar.
  void moHopThoaiThongBao() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.notifications_active, color: Colors.blueAccent),
            SizedBox(width: 8),
            Text('Thông báo hệ thống'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('• Đề thi thử ETS 2024 mới đã được cập nhật!'),
            SizedBox(height: 8),
            Text('• Đừng quên hoàn thành nhiệm vụ ngày để duy trì Streak.'),
            SizedBox(height: 8),
            Text('• Tính năng Đọc tiếng Anh & Dịch AI đã sẵn sàng hỗ trợ bạn.'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Đã hiểu'),
          ),
        ],
      ),
    );
  }

  /// HAM TIEN ICH: hienThongBao()
  /// WIDGET: SnackBar & ScaffoldMessenger
  /// Hoat dong: Hien thi pop-up ngan o day man hinh phan hoi thao tac.
  void hienThongBao(String noiDung) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(noiDung),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// HAM TIEN ICH: moManHinh()
  /// WIDGET: Navigator.push
  /// Hoat dong: Dieu huong den mot man hinh con doc lap (nhu Chat AI, Luyen doc, So tay).
  void moManHinh(Widget manHinhMoi) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => manHinhMoi),
    );
  }

  /// GIAO DIEN CON: xayDungGiaoDienTrangChu()
  /// Vai tro: Tra ve toan bo giao dien Dashboard cua Tab 0 (Trang chu).
  Widget xayDungGiaoDienTrangChu() {
    // WIDGET: SingleChildScrollView
    // Cho phep cuon toan bo noi dung Dashboard khi man hinh co kich thuoc nho
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // WIDGET: Card
          // The xanh noi bat tren cung hien thi loi chao, chuoi Streak, va 3 chi so tong quan
          Card(
            elevation: 3,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: Colors.blueAccent,
            child: Padding(
              padding: const EdgeInsets.all(18.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Xin chào, Học viên!',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Mục tiêu: TOEIC 750+',
                            style: TextStyle(color: Colors.white70, fontSize: 14),
                          ),
                        ],
                      ),

                      // WIDGET: InkWell
                      // Tao vung nhan nut cho phep click de diem danh Streak ngay
                      InkWell(
                        onTap: diemDanhHangNgay,
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.local_fire_department, color: Colors.deepOrange),
                              const SizedBox(width: 4),
                              Text(
                                '$soNgayHocLienTiep Ngày',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.deepOrange,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: Colors.white30),
                  const SizedBox(height: 8),

                  // Hang 3 thong so: So cau da lam - So tu da thuoc - Ty le dung
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          Text('142', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                          Text('Câu đã làm', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                      Column(
                        children: [
                          Text('85', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                          Text('Từ đã thuộc', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                      Column(
                        children: [
                          Text('76%', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                          Text('Tỷ lệ đúng', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // WIDGET: Card (Banner Test dau vao)
          // The mau vang noi bat giup hoc vien nhap vao de lam bai kiem tra trinh do dau vao (Placement Test)
          Card(
            color: Colors.amber[50],
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: Colors.amber, width: 1.2),
            ),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Row(
                children: [
                  const CircleAvatar(
                    backgroundColor: Colors.amber,
                    radius: 22,
                    child: Icon(Icons.psychology, color: Colors.white, size: 26),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Test trình độ đầu vào',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.black87),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Làm bài test 45 phút để đánh giá điểm mạnh, điểm yếu và lên lộ trình riêng.',
                          style: TextStyle(color: Colors.grey[700], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => moManHinh(const KiemTraDauVaoManHinh()),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.amber[800],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                    child: const Text('Test ngay'),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          const Text(
            'Chức năng chính',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          // WIDGET: GridView.count
          // Vai tro: Bo cuc dang luoi chia thanh 2 cot deu nhau (crossAxisCount: 2).
          // shrinkWrap: true va physics: NeverScrollableScrollPhysics giup GridView nam gon ben trong
          // SingleChildScrollView ma khong bi xung dot cuon chuot.
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.35,
            children: [
              _xayDungTheChucNang(
                tieuDe: 'Luyện tập Part 1-7',
                moTa: 'Làm câu hỏi theo từng phần',
                bieuTuong: Icons.menu_book,
                mauSac: Colors.orange,
                khiBam: () => chuyenTab(1), // Chuyen sang Tab 1 o thanh dieu huong
              ),
              _xayDungTheChucNang(
                tieuDe: 'Thi thử TOEIC',
                moTa: 'Đề thi chuẩn format ETS',
                bieuTuong: Icons.assignment,
                mauSac: Colors.green,
                khiBam: () => chuyenTab(2), // Chuyen sang Tab 2
              ),
              _xayDungTheChucNang(
                tieuDe: 'Lật thẻ từ vựng',
                moTa: 'Flashcard 600 từ TOEIC',
                bieuTuong: Icons.style,
                mauSac: Colors.purple,
                khiBam: () => chuyenTab(3), // Chuyen sang Tab 3
              ),
              _xayDungTheChucNang(
                tieuDe: 'Đọc tiếng Anh & AI',
                moTa: 'Luyện đọc & Dịch thông minh',
                bieuTuong: Icons.translate,
                mauSac: Colors.teal,
                khiBam: () => moManHinh(const LuyenDocVaDichManHinh()),
              ),
              _xayDungTheChucNang(
                tieuDe: 'Lộ trình học tập',
                moTa: 'Kế hoạch chinh phục 750+',
                bieuTuong: Icons.alt_route,
                mauSac: Colors.indigo,
                khiBam: () => moManHinh(const LoTrinhHocManHinh()),
              ),
              _xayDungTheChucNang(
                tieuDe: 'Trợ lý gia sư AI',
                moTa: 'Hỏi đáp giải thích ngữ pháp',
                bieuTuong: Icons.smart_toy,
                mauSac: Colors.pink,
                khiBam: () => moManHinh(const TroLyAiManHinh()),
              ),
              _xayDungTheChucNang(
                tieuDe: 'Sổ tay câu sai',
                moTa: 'Ôn tập lại các câu đã sai',
                bieuTuong: Icons.bookmark_border,
                mauSac: Colors.redAccent,
                khiBam: () => moManHinh(const SoTayOnTapManHinh()),
              ),
              _xayDungTheChucNang(
                tieuDe: 'Tiến độ & Cài đặt',
                moTa: 'Báo cáo và thiết lập app',
                bieuTuong: Icons.settings,
                mauSac: Colors.blueGrey,
                khiBam: () => chuyenTab(4), // Chuyen sang Tab 4
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Danh sach nhiem vu hom nay
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Nhiệm vụ hôm nay',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              Text(
                '${danhSachNhiemVu.where((n) => n['hoanThanh'] == true).length}/${danhSachNhiemVu.length} hoàn thành',
                style: TextStyle(color: Colors.grey[600], fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // WIDGET: ListView.builder
          // Vai tro: Xay dung danh sach cac the nhiem vu hang ngay mot cach toi uu bo nho
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: danhSachNhiemVu.length,
            itemBuilder: (context, index) {
              final nhiemVu = danhSachNhiemVu[index];
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 4),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                // WIDGET: CheckboxListTile
                // Vai tro: Ket hop san mot hop Checkbox voi tieu de Title va chip diem thuong Secondary.
                child: CheckboxListTile(
                  value: nhiemVu['hoanThanh'],
                  onChanged: (bool? giaTri) => hoanThanhNhiemVu(index),
                  title: Text(
                    nhiemVu['tieuDe'],
                    style: TextStyle(
                      decoration: nhiemVu['hoanThanh'] ? TextDecoration.lineThrough : null, // Gach ngang khi da xong
                      color: nhiemVu['hoanThanh'] ? Colors.grey : Colors.black87,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  // WIDGET: Chip
                  // Vai tro: Huy hieu nho hien thi so diem thuong XP khi hoan thanh
                  secondary: Chip(
                    label: Text(
                      nhiemVu['diem'],
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                    backgroundColor: Colors.amber[100],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  /// HELPER WIDGET: _xayDungTheChucNang()
  /// Vai tro: Tao the Card dai dien cho tung tinh nang voi bieu tuong bo tron CircleAvatar va hieu ung click InkWell.
  Widget _xayDungTheChucNang({
    required String tieuDe,
    required String moTa,
    required IconData bieuTuong,
    required Color mauSac,
    required VoidCallback khiBam,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: khiBam,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // WIDGET: CircleAvatar
              // Hinh tron chua bieu tuong mau sac dai dien cho tinh nang
              CircleAvatar(
                radius: 20,
                backgroundColor: mauSac.withOpacity(0.15),
                child: Icon(bieuTuong, color: mauSac, size: 22),
              ),
              const SizedBox(height: 8),
              Text(
                tieuDe,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 2),
              Text(
                moTa,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(color: Colors.grey[600], fontSize: 11),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Danh sach cac widget man hinh tuong ung voi 5 tab cua BottomNavigationBar
    final List<Widget> danhSachCacTab = [
      xayDungGiaoDienTrangChu(),
      const LuyenTapManHinh(),
      const ThiThuManHinh(),
      const TuVungLatTheManHinh(),
      const TienDoVaCaiDatManHinh(),
    ];

    // WIDGET: Scaffold
    // Khung giao dien tong the cua toan man hinh chinh
    return Scaffold(
      // WIDGET: AppBar
      // Thanh tieu de tren cung, tieu de tu dong thay doi ten theo tab dang chon
      appBar: AppBar(
        title: Text(
          viTriTabHienTai == 0
              ? 'GetGoals Dashboard'
              : viTriTabHienTai == 1
                  ? 'Luyện tập TOEIC'
                  : viTriTabHienTai == 2
                      ? 'Thi thử TOEIC'
                      : viTriTabHienTai == 3
                          ? 'Từ vựng Flashcard'
                          : 'Tiến độ & Cài đặt',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          // Nut chuong thong bao
          IconButton(
            icon: const Icon(Icons.notifications_none),
            tooltip: 'Thông báo',
            onPressed: moHopThoaiThongBao,
          ),
          // Nut mo nhanh Tro ly gia su AI
          IconButton(
            icon: const Icon(Icons.smart_toy_outlined),
            tooltip: 'Trợ lý AI',
            onPressed: () => moManHinh(const TroLyAiManHinh()),
          ),
        ],
      ),

      // Phan Body: Hien thi man hinh tuong ung voi chi so tab viTriTabHienTai
      body: danhSachCacTab[viTriTabHienTai],

      // WIDGET: BottomNavigationBar
      // Vai tro: Thanh dieu huong 5 tab nam co dinh o day man hinh.
      // currentIndex: Tab hien tai duoc to sang (mau blueAccent).
      // onTap: Khi nguoi dung bam vao mot tab bat ky, goi ham chuyenTab de cap nhat viTriTabHienTai.
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: viTriTabHienTai,
        onTap: chuyenTab,
        type: BottomNavigationBarType.fixed, // Giu nguyen kich thuoc cho ca 5 tab
        selectedItemColor: Colors.blueAccent, // Mau cua tab dang duoc chon
        unselectedItemColor: Colors.grey,     // Mau cua cac tab con lai
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Trang chủ',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book),
            label: 'Luyện tập',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment),
            label: 'Thi thử',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.style),
            label: 'Từ vựng',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Tài khoản',
          ),
        ],
      ),
    );
  }
}
