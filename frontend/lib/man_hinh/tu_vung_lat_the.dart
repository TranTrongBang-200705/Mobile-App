import 'package:flutter/material.dart';

/// MAN HINH: TuVungLatTheManHinh
/// Ke thua StatefulWidget vi can quan ly tuong tac the hoc Flashcard:
/// - chuDeDangChon: Chu de tu vung dang xem
/// - chiSoTheHienTai: Tu vung hien tai trong mang danh sach
/// - dangXemMatSau: Trang thai the dang mo Mat truoc (tieng Anh) hay Mat sau (nghia tieng Viet)
/// - soTuDaThuoc / soTuChuaThuoc: Bo dem thong ke trong phien hoc
class TuVungLatTheManHinh extends StatefulWidget {
  const TuVungLatTheManHinh({super.key});

  @override
  State<TuVungLatTheManHinh> createState() => _TuVungLatTheManHinhState();
}

class _TuVungLatTheManHinhState extends State<TuVungLatTheManHinh> {
  // BIEN TRANG THAI (STATE):
  String chuDeDangChon = 'Business & Cong so';
  int chiSoTheHienTai = 0;
  bool dangXemMatSau = false; // false: Mat truoc (Tieng Anh), true: Mat sau (Tieng Viet)

  int soTuDaThuoc = 0;
  int soTuChuaThuoc = 0;

  // Danh sach cac chu de tu vung
  final List<String> danhSachChuDe = [
    'Business & Cong so',
    'Du lich & Giao thong',
    'Mua sam & Gia ca',
    'Nha hang & An uong',
    'Cong nghe & Van phong',
  ];

  // Danh sach tu vung mau cua chu de Business
  List<Map<String, String>> danhSachTuVung = [
    {
      'tu': 'Negotiate',
      'phienAm': '/nɪˈɡoʊ.ʃi.eɪt/',
      'loaiTu': 'Dong tu (v)',
      'nghia': 'Dam phan, thuong luong',
      'viDu': 'The company is negotiating a new contract with suppliers.',
      'dichViDu': 'Cong ty dang dam phan mot hop dong moi voi cac nha cung cap.',
    },
    {
      'tu': 'Revenue',
      'phienAm': '/ˈrev.ə.nuː/',
      'loaiTu': 'Danh tu (n)',
      'nghia': 'Doanh thu, thu nhap',
      'viDu': 'Total company revenue increased by 15% this quarter.',
      'dichViDu': 'Tong doanh thu cong ty da tang 15% trong quy nay.',
    },
    {
      'tu': 'Implement',
      'phienAm': '/ˈɪm.plə.ment/',
      'loaiTu': 'Dong tu (v)',
      'nghia': 'Trien khai, thuc thi',
      'viDu': 'We need to implement these changes as soon as possible.',
      'dichViDu': 'Chung ta can trien khai nhung thay doi nay cang som cang tot.',
    },
    {
      'tu': 'Merger',
      'phienAm': '/ˈmɜː.dʒər/',
      'loaiTu': 'Danh tu (n)',
      'nghia': 'Su sap nhap doanh nghiep',
      'viDu': 'The proposed merger will create a global telecom leader.',
      'dichViDu': 'Thuong vu sap nhap du kien se tao ra mot ong lon vien thong toan cau.',
    },
    {
      'tu': 'Promising',
      'phienAm': '/ˈprɑː.mɪ.sɪŋ/',
      'loaiTu': 'Tinh tu (adj)',
      'nghia': 'Day trien vong, hua hen',
      'viDu': 'She is one of the most promising young managers in the team.',
      'dichViDu': 'Co ay la mot trong nhung nha quan ly tre day trien vong nhat doi.',
    },
  ];

  /// HAM XU LY: latTheTuVung()
  /// Hoat dong: Dao nguoc bien dangXemMatSau de lat mat the flashcard.
  void latTheTuVung() {
    setState(() {
      dangXemMatSau = !dangXemMatSau;
    });
  }

  /// HAM XU LY: chuyenTheTiepTheo()
  /// Hoat dong: Chuyen sang the ke tiep va reset mat the ve mat truoc (tieng Anh).
  void chuyenTheTiepTheo() {
    if (chiSoTheHienTai < danhSachTuVung.length - 1) {
      setState(() {
        chiSoTheHienTai++;
        dangXemMatSau = false;
      });
    } else {
      hienThongBao('Ban da hoan thanh danh sach tu cua chu de nay!');
    }
  }

  /// HAM XU LY: quayLaiTheTruoc()
  /// Hoat dong: Quay tro lai the tu vung truoc do.
  void quayLaiTheTruoc() {
    if (chiSoTheHienTai > 0) {
      setState(() {
        chiSoTheHienTai--;
        dangXemMatSau = false;
      });
    }
  }

  /// HAM XU LY: danhDauDaThuoc()
  /// Hoat dong: Tang soTuDaThuoc va tu dong chuyen the tiep theo.
  void danhDauDaThuoc() {
    setState(() {
      soTuDaThuoc++;
    });
    hienThongBao('Tuyet voi! Da them vao danh sach Tu da thuoc.');
    chuyenTheTiepTheo();
  }

  /// HAM XU LY: danhDauChuaThuoc()
  /// Hoat dong: Tang soTuChuaThuoc de luu vao danh sach can on lai.
  void danhDauChuaThuoc() {
    setState(() {
      soTuChuaThuoc++;
    });
    hienThongBao('Da danh dau! Tu nay se xuat hien lai trong buoi on.');
    chuyenTheTiepTheo();
  }

  /// HAM XU LY: xaoTronDanhSach()
  /// Hoat dong: Su dung ham shuffle() cua List de xao tron thu tu ngau nhien giup nho tu tot hon.
  void xaoTronDanhSach() {
    setState(() {
      danhSachTuVung.shuffle();
      chiSoTheHienTai = 0;
      dangXemMatSau = false;
    });
    hienThongBao('Da xao tron danh sach tu vung!');
  }

  /// HAM XU LY: doiChuDeTuVung()
  /// Hoat dong: Cap nhat chu de moi khi nguoi dung chon tren DropdownButton.
  void doiChuDeTuVung(String chuDeMoi) {
    setState(() {
      chuDeDangChon = chuDeMoi;
      chiSoTheHienTai = 0;
      dangXemMatSau = false;
    });
    hienThongBao('Da chuyen sang chu de: $chuDeMoi');
  }

  /// HAM TIEN ICH: giaLapPhatAm()
  void giaLapPhatAm(String tu) {
    hienThongBao('Dang phat am: "$tu" (Audio US/UK)');
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
    final tuHienTai = danhSachTuVung[chiSoTheHienTai];

    // WIDGET: Scaffold
    // Khung man hinh co ban
    return Scaffold(
      // WIDGET: SingleChildScrollView
      // Cho phep cuon toan bo noi dung flashcard
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // WIDGET: Row & DropdownButton
            // Vai tro: Menu xo xuong cho phep chon nhom chu de tu vung
            Row(
              children: [
                const Icon(Icons.category_outlined, color: Colors.blueAccent),
                const SizedBox(width: 8),
                Expanded(
                  // WIDGET: DropdownButton
                  // Menu lua chon gia tri trong danh sach danhSachChuDe
                  child: DropdownButton<String>(
                    isExpanded: true,
                    value: chuDeDangChon,
                    items: danhSachChuDe.map((String cDe) {
                      return DropdownMenuItem<String>(
                        value: cDe,
                        child: Text(cDe, style: const TextStyle(fontWeight: FontWeight.bold)),
                      );
                    }).toList(),
                    onChanged: (String? giaTriMoi) {
                      if (giaTriMoi != null) doiChuDeTuVung(giaTriMoi);
                    },
                  ),
                ),
                // Nut xao tron the
                IconButton(
                  icon: const Icon(Icons.shuffle, color: Colors.blueAccent),
                  tooltip: 'Xao tron the',
                  onPressed: xaoTronDanhSach,
                ),
              ],
            ),

            const SizedBox(height: 12),

            // WIDGET: Row
            // Thanh thong ke so thu tu the hien tai va so tu da thuoc / chua thuoc
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'The ${chiSoTheHienTai + 1} / ${danhSachTuVung.length}',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                Row(
                  children: [
                    Text('Da thuoc: $soTuDaThuoc', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 12),
                    Text('Chua thuoc: $soTuChuaThuoc', style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 16),

            // WIDGET: GestureDetector & AnimatedContainer (THE FLASHCARD LAT MAT)
            // Vai tro:
            // 1. GestureDetector bat su kien cham onTap de goi latTheTuVung().
            // 2. AnimatedContainer tao hieu ung chuyen doi mau sac va do bong em diu trong 300 mili-giay.
            GestureDetector(
              onTap: latTheTuVung,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300), // Thoi gian chay animation
                height: 280,
                decoration: BoxDecoration(
                  // Doi mau nen: Mat truoc la xanh nhat (blue[50]), mat sau la vang nhat (amber[50])
                  color: dangXemMatSau ? Colors.amber[50] : Colors.blue[50],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: dangXemMatSau ? Colors.orangeAccent : Colors.blueAccent,
                    width: 2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.08),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(20),
                child: Center(
                  // CO CHE DIEU KIEN: Hien thi Mat sau hoac Mat truoc
                  child: dangXemMatSau
                      // GIAO DIEN MAT SAU: NGHIA TIENG VIET & VI DU MINH HOA
                      ? Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              'NGHIA TIENG VIET',
                              style: TextStyle(fontSize: 12, color: Colors.orange, fontWeight: FontWeight.bold, letterSpacing: 1.2),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              tuHienTai['nghia']!,
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black87),
                            ),
                            const Divider(height: 28),
                            Text(
                              'Vi du: "${tuHienTai['viDu']}"',
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 14, fontStyle: FontStyle.italic),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              tuHienTai['dichViDu']!,
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                            ),
                            const SizedBox(height: 12),
                            const Text(
                              '(Cham de quay ve mat truoc)',
                              style: TextStyle(fontSize: 11, color: Colors.grey),
                            ),
                          ],
                        )
                      // GIAO DIEN MAT TRUOC: TU TIENG ANH, LOAI TU & PHIEN AM IPA
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Chip(
                              label: Text(tuHienTai['loaiTu']!),
                              backgroundColor: Colors.white,
                            ),
                            const SizedBox(height: 12),
                            Text(
                              tuHienTai['tu']!,
                              style: const TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: Colors.blueAccent,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              tuHienTai['phienAm']!,
                              style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                            ),
                            const SizedBox(height: 16),
                            // Nut nghe phat am
                            IconButton(
                              icon: const Icon(Icons.volume_up, color: Colors.blueAccent, size: 32),
                              tooltip: 'Nghe phat am',
                              onPressed: () => giaLapPhatAm(tuHienTai['tu']!),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              '(Cham the de xem nghia tieng Viet)',
                              style: TextStyle(fontSize: 11, color: Colors.grey),
                            ),
                          ],
                        ),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // WIDGET: Row & ElevatedButton.icon
            // Hai nut hanh dong quan trong: "Chua thuoc" (mau do) va "Da thuoc" (mau xanh la)
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: danhDauChuaThuoc,
                    icon: const Icon(Icons.replay),
                    label: const Text('Chua thuoc'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.redAccent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: danhDauDaThuoc,
                    icon: const Icon(Icons.check),
                    label: const Text('Da thuoc'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Hang nut dieu huong: Tu truoc - Lat the - Tu sau
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  onPressed: quayLaiTheTruoc,
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Tu truoc'),
                ),
                TextButton.icon(
                  onPressed: latTheTuVung,
                  icon: const Icon(Icons.flip),
                  label: const Text('Lat the'),
                ),
                OutlinedButton.icon(
                  onPressed: chuyenTheTiepTheo,
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('Tu sau'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
