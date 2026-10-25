import 'package:flutter/material.dart';

/// MAN HINH: LuyenDocVaDichManHinh
/// Ke thua StatefulWidget va su dung mixin SingleTickerProviderStateMixin vi co bo dieu khien TabController
/// giup tao hieu ung chuyen dong muot ma giua 2 Tab:
/// 1. Tab Luyen doc doan van co giong doc am thanh
/// 2. Tab Dich thuat AI thong minh da chieu
class LuyenDocVaDichManHinh extends StatefulWidget {
  const LuyenDocVaDichManHinh({super.key});

  @override
  State<LuyenDocVaDichManHinh> createState() => _LuyenDocVaDichManHinhState();
}

class _LuyenDocVaDichManHinhState extends State<LuyenDocVaDichManHinh> with SingleTickerProviderStateMixin {
  // OBJECT: TabController
  // Vai tro: Dieu khien dong bo giua thanh tieu de TabBar va vung noi dung TabBarView
  late TabController boDieuKhienTab;

  // Trang thai phat am thanh bai doc
  bool dangPhatAmThanh = false;

  // Controller quan ly o nhap van ban dich
  final TextEditingController oNhapVanBanController = TextEditingController();
  String banDichKetQua = '';
  bool chieuDichAnhSangViet = true;
  bool dangXuLyDich = false;

  // Du lieu doan van tieng Anh mau
  final String tieuDeBaiDoc = 'Company Announcement: Annual General Meeting';
  final String noiDungBaiDoc =
      'To all esteemed colleagues and shareholders, we are pleased to announce that our Annual General Meeting (AGM) will take place next month. '
      'The board of directors will discuss financial milestones, product expansions, and upcoming technological investments. '
      'All attendees are required to register in advance through our official company portal.';

  @override
  void initState() {
    super.initState();
    // Khoi tao TabController voi 2 tab va vsync la chinh State hien tai
    boDieuKhienTab = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    boDieuKhienTab.dispose();
    oNhapVanBanController.dispose();
    super.dispose();
  }

  /// HAM XU LY: chuyenTrangThaiPhatAm()
  /// Hoat dong: Bat hoac tat giong doc am thanh gia lap cho bai doc tieng Anh.
  void chuyenTrangThaiPhatAm() {
    setState(() {
      dangPhatAmThanh = !dangPhatAmThanh;
    });
    if (dangPhatAmThanh) {
      hienThongBao('Dang phat giong doc tieng Anh ban xu (US Accent)...');
    } else {
      hienThongBao('Da tam dung giong doc.');
    }
  }

  /// HAM XU LY: traCuuTuNhanh()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Khi nguoi dung bam vao mot tu vung bat ky trong bai doc, hop thoai hien len giai nghia nhanh va cho phep luu tu.
  void traCuuTuNhanh(String tuTiengAnh, String nghia) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.menu_book, color: Colors.blueAccent),
            const SizedBox(width: 8),
            Text(tuTiengAnh, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        content: Text('Nghia: $nghia', style: const TextStyle(fontSize: 16)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Dong'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context);
              hienThongBao('Da luu "$tuTiengAnh" vao danh sach tu can on!');
            },
            icon: const Icon(Icons.bookmark_add),
            label: const Text('Luu tu nay'),
          ),
        ],
      ),
    );
  }

  /// HAM XU LY: xuLyDichThuat()
  /// CO CHE: Future.delayed
  /// Hoat dong: Tao do tre 500 mili-giay mo phong thoi gian may chu AI phan tich ngu nghia va tra ve ban dich.
  void xuLyDichThuat() {
    final vanBan = oNhapVanBanController.text.trim();
    if (vanBan.isEmpty) {
      hienThongBao('Vui long nhap doan van can dich!');
      return;
    }

    setState(() {
      dangXuLyDich = true;
    });

    Future.delayed(const Duration(milliseconds: 500), () {
      if (!mounted) return;
      setState(() {
        dangXuLyDich = false;
        if (chieuDichAnhSangViet) {
          banDichKetQua =
              'Ban dich AI: "Chung toi rat vui mung thong bao rang cuoc hop thuong nien se dien ra vao thang toi. Ban giam doc se thao luan ve cac moc tai chinh quan trong va ke hoach mo rong quy mo."';
        } else {
          banDichKetQua =
              'AI Translation: "We are pleased to inform you that our upcoming conference will commence next week with international delegates."';
        }
      });
      hienThongBao('Dich thuat AI hoan tat!');
    });
  }

  /// HAM XU LY: doiChieuDich()
  /// Hoat dong: Hoan doi chieu dich giua Tieng Anh -> Tieng Viet va Tieng Viet -> Tieng Anh.
  void doiChieuDich() {
    setState(() {
      chieuDichAnhSangViet = !chieuDichAnhSangViet;
      banDichKetQua = '';
    });
    hienThongBao(chieuDichAnhSangViet ? 'Chieu dich: Tieng Anh -> Tieng Viet' : 'Chieu dich: Tieng Viet -> Tieng Anh');
  }

  /// HAM XU LY: xoaNoiDungNhap()
  void xoaNoiDungNhap() {
    oNhapVanBanController.clear();
    setState(() {
      banDichKetQua = '';
    });
    hienThongBao('Da xoa van ban.');
  }

  /// HAM XU LY: saoChepKetQua()
  void saoChepKetQua() {
    if (banDichKetQua.isEmpty) return;
    hienThongBao('Da sao chep ban dich vao bo nho tam!');
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
    // Khung giao dien chinh
    return Scaffold(
      // WIDGET: AppBar voi TabBar o bottom
      // Vai tro: Dat 2 tab o ngay duoi tieu de AppBar de nguoi dung tien chuyen doi
      appBar: AppBar(
        title: const Text('Doc & Dich AI'),
        // WIDGET: TabBar
        // Thanh dieu khien tab gom 2 Tab: Luyen doc va Dich thuat AI
        bottom: TabBar(
          controller: boDieuKhienTab,
          tabs: const [
            Tab(icon: Icon(Icons.chrome_reader_mode), text: 'Luyen doc bai van'),
            Tab(icon: Icon(Icons.translate), text: 'Dich thuat AI'),
          ],
        ),
      ),

      // WIDGET: TabBarView
      // Vai tro: Khu vuc hien thi noi dung cua tung tab tuong ung voi boDieuKhienTab.
      // Cho phep nguoi dung vuot ngang bang tay (Swipe Gesture) de chuyen giua 2 man hinh.
      body: TabBarView(
        controller: boDieuKhienTab,
        children: [
          // ==================== TAB 1: LUYEN DOC BAI VAN VA NGHE GIONG DOC ====================
          SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // The Card chua noi dung bai doc va nut phat am thanh
                Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                tieuDeBaiDoc,
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blueAccent),
                              ),
                            ),
                            // Nut phat / tam dung audio
                            IconButton(
                              icon: Icon(
                                dangPhatAmThanh ? Icons.pause_circle_filled : Icons.play_circle_fill,
                                size: 36,
                                color: dangPhatAmThanh ? Colors.orange : Colors.blueAccent,
                              ),
                              tooltip: dangPhatAmThanh ? 'Tam dung' : 'Phat audio',
                              onPressed: chuyenTrangThaiPhatAm,
                            ),
                          ],
                        ),
                        if (dangPhatAmThanh)
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 8),
                            child: LinearProgressIndicator(),
                          ),
                        const Divider(height: 24),
                        Text(
                          noiDungBaiDoc,
                          style: const TextStyle(fontSize: 16, height: 1.6),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // WIDGET: Wrap & ActionChip
                // Vai tro: Wrap giup cac the tu vung tu dong xuong dong khi vuot qua be ngang man hinh.
                // ActionChip: Chip co the bam duoc, khi bam se goi traCuuTuNhanh().
                const Text(
                  'Tu khoa quan trong (Nhan vao de tra nghia):',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ActionChip(
                      avatar: const Icon(Icons.search, size: 16),
                      label: const Text('esteemed'),
                      onPressed: () => traCuuTuNhanh('esteemed', 'Dang kinh, duoc coi trong'),
                    ),
                    ActionChip(
                      avatar: const Icon(Icons.search, size: 16),
                      label: const Text('shareholders'),
                      onPressed: () => traCuuTuNhanh('shareholders', 'Co dong cong ty'),
                    ),
                    ActionChip(
                      avatar: const Icon(Icons.search, size: 16),
                      label: const Text('milestones'),
                      onPressed: () => traCuuTuNhanh('milestones', 'Cac cot moc, thanh tuu quan trong'),
                    ),
                    ActionChip(
                      avatar: const Icon(Icons.search, size: 16),
                      label: const Text('attendees'),
                      onPressed: () => traCuuTuNhanh('attendees', 'Nguoi tham du'),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // ==================== TAB 2: DICH THUAT AI THONG MINH ====================
          SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Thanh chuyen doi chieu ngon ngu
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      chieuDichAnhSangViet ? 'Tieng Anh' : 'Tieng Viet',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    IconButton(
                      icon: const Icon(Icons.swap_horiz, color: Colors.blueAccent),
                      tooltip: 'Doi chieu dich',
                      onPressed: doiChieuDich,
                    ),
                    Text(
                      chieuDichAnhSangViet ? 'Tieng Viet' : 'Tieng Anh',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // WIDGET: TextField
                // maxLines: 4 giup tao o nhap nhieu dong (TextArea) de dan ca doan van dai vao dich
                TextField(
                  controller: oNhapVanBanController,
                  maxLines: 4,
                  decoration: InputDecoration(
                    hintText: chieuDichAnhSangViet ? 'Nhap van ban tieng Anh can dich vao day...' : 'Nhap van ban tieng Viet...',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: xoaNoiDungNhap,
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // WIDGET: ElevatedButton.icon
                // Nut kich hoat tri tue nhan tao AI dich doan van
                ElevatedButton.icon(
                  onPressed: dangXuLyDich ? null : xuLyDichThuat,
                  icon: const Icon(Icons.auto_awesome),
                  label: Text(dangXuLyDich ? 'Dang phan tich dich...' : 'DICH NGAY BANG AI'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
                const SizedBox(height: 16),

                // Khung ket qua ban dich AI
                if (banDichKetQua.isNotEmpty) ...[
                  Card(
                    color: Colors.green[50],
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'KET QUA BAN DICH AI',
                                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 13),
                              ),
                              IconButton(
                                icon: const Icon(Icons.copy, size: 20),
                                tooltip: 'Sao chep ket qua',
                                onPressed: saoChepKetQua,
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            banDichKetQua,
                            style: const TextStyle(fontSize: 16, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
