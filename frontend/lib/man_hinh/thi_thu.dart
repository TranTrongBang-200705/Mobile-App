import 'dart:async';
import 'package:flutter/material.dart';

/// MAN HINH: ThiThuManHinh
/// Ke thua StatefulWidget vi can quan ly phong thi thu thoi gian thuc:
/// - Timer bo dem nguoc thoi gian lam bai (thoiGianConLai)
/// - Danh sach dap an cua 20 cau hoi (danhSachDapAnDaChon)
/// - Danh sach cac cau hoi duoc danh dau co xem lai (danhSachDanhDau)
/// - Chuyen doi giua giao dien Danh sach de thi va Phong lam bai
class ThiThuManHinh extends StatefulWidget {
  const ThiThuManHinh({super.key});

  @override
  State<ThiThuManHinh> createState() => _ThiThuManHinhState();
}

class _ThiThuManHinhState extends State<ThiThuManHinh> {
  // BIEN TRANG THAI (STATE):
  bool dangLamBai = false; // false: dang xem danh sach de; true: dang trong phong thi
  String tenDeThiHienTai = 'ETS TOEIC 2024 - Test 01';

  // CO CHE DONG HO DEM NGUOC:
  // Timer: Su dung thu vien dart:async de tao bo dem giay dem nguoc tuong tu dong ho phong thi that
  int thoiGianConLai = 1800; // 30 phut = 1800 giay
  Timer? boDemThoiGian;
  bool dangTamDung = false;

  int cauHienTai = 0; // Chi so cau hoi dang xem (0 den 19)
  late List<int> danhSachDapAnDaChon; // Luu lua chon cua 20 cau (-1 la chua chon)
  late List<bool> danhSachDanhDau;    // Danh dau Flag xem lai

  // 20 cau hoi mau format TOEIC
  final List<Map<String, dynamic>> duLieuCauHoiThiThu = List.generate(20, (index) {
    return {
      'soCau': index + 1,
      'phan': index < 10 ? 'Listening (Part 1 - 4)' : 'Reading (Part 5 - 7)',
      'noiDung': 'Question ${index + 1}: The executive board decided to _____ the proposed merger until the next quarterly meeting.',
      'cacLuaChon': ['A. postpone', 'B. postponed', 'C. postponement', 'D. postponing'],
      'dapAnDung': 0, // A
    };
  });

  @override
  void initState() {
    super.initState();
    // Khoi tao mang 20 phan tu mac dinh -1 (chua lam) va false (chua danh dau)
    danhSachDapAnDaChon = List.filled(20, -1);
    danhSachDanhDau = List.filled(20, false);
  }

  @override
  void dispose() {
    // Huy bo dem Timer khi roi khoi man hinh de tiet kiem pin va tranh memory leak
    boDemThoiGian?.cancel();
    super.dispose();
  }

  /// HAM XU LY: batDauThiThu()
  /// CO CHE: Timer.periodic
  /// Hoat dong: Khoi dong bo dem giay chay ngam moi 1 giay giam bien thoiGianConLai di 1.
  /// Khi thoiGianConLai == 0 thi tu dong goi xacNhanNopBai() de thu bai va cham diem.
  void batDauThiThu(String tenDe, int soPhut) {
    setState(() {
      tenDeThiHienTai = tenDe;
      dangLamBai = true;
      thoiGianConLai = soPhut * 60;
      dangTamDung = false;
      cauHienTai = 0;
      danhSachDapAnDaChon = List.filled(20, -1);
      danhSachDanhDau = List.filled(20, false);
    });

    boDemThoiGian?.cancel();
    boDemThoiGian = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!dangTamDung) {
        if (thoiGianConLai > 0) {
          setState(() {
            thoiGianConLai--;
          });
        } else {
          timer.cancel();
          xacNhanNopBai(tuDong: true);
        }
      }
    });
  }

  /// HAM XU LY: tamDungHoacTiepTuc()
  /// Hoat dong: Tam dung hoac tiep tuc dem giay khi thi sinh can nghi ngoi giua gio.
  void tamDungHoacTiepTuc() {
    setState(() {
      dangTamDung = !dangTamDung;
    });
    hienThongBao(dangTamDung ? 'Da tam dung bai thi!' : 'Tiep tuc tinh gio!');
  }

  /// HAM XU LY: chonCauHoi()
  /// Hoat dong: Nhay nhanh den cau bat ky khi nguoi dung bam vao o so tren thanh luoi cau hoi.
  void chonCauHoi(int index) {
    setState(() {
      cauHienTai = index;
    });
  }

  /// HAM XU LY: chonDapAn()
  /// Hoat dong: Ghi nhan lua chon A, B, C, D vao mang danhSachDapAnDaChon tai vi tri cauHienTai.
  void chonDapAn(int indexDapAn) {
    setState(() {
      danhSachDapAnDaChon[cauHienTai] = indexDapAn;
    });
  }

  /// HAM XU LY: danhDauXemLai()
  /// Hoat dong: Bat / tat co Flag danh dau cau hoi phan van de xem lai sau.
  void danhDauXemLai() {
    setState(() {
      danhSachDanhDau[cauHienTai] = !danhSachDanhDau[cauHienTai];
    });
    hienThongBao(danhSachDanhDau[cauHienTai]
        ? 'Da danh dau cau ${cauHienTai + 1} de xem lai.'
        : 'Da bo danh dau cau ${cauHienTai + 1}.');
  }

  /// HAM XU LY: xacNhanNopBai()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Bat popup kiem tra so cau da lam / tong so cau va yeu cau xac nhan truoc khi cham diem.
  void xacNhanNopBai({bool tuDong = false}) {
    if (tuDong) {
      hienKetQuaThi();
      return;
    }

    int soCauDaLam = danhSachDapAnDaChon.where((da) => da != -1).length;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Xac nhan nop bai'),
        content: Text(
          'Ban da hoan thanh $soCauDaLam/20 cau hoi.\nBan co chac chan muon nop bai thi ngay khong?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Lam tiep'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () {
              Navigator.pop(context);
              hienKetQuaThi();
            },
            child: const Text('Nop bai ngay', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  /// HAM XU LY: hienKetQuaThi()
  /// Hoat dong: Dung Timer, tinh so cau dung, uoc luong diem Listening va Reading theo bang diem TOEIC chuan,
  /// va hien thi AlertDialog tong ket diem so.
  void hienKetQuaThi() {
    boDemThoiGian?.cancel();

    int soCauDung = 0;
    for (int i = 0; i < duLieuCauHoiThiThu.length; i++) {
      if (danhSachDapAnDaChon[i] == duLieuCauHoiThiThu[i]['dapAnDung']) {
        soCauDung++;
      }
    }

    // Tinh diem uoc luong TOEIC thang 990
    int diemListening = (soCauDung * 22) + 50;
    if (diemListening > 495) diemListening = 495;
    int diemReading = (soCauDung * 20) + 40;
    if (diemReading > 495) diemReading = 495;
    int tongDiem = diemListening + diemReading;

    showDialog(
      context: context,
      barrierDismissible: false, // Bat buoc nguoi dung phai bam nut hoan thanh tren popup
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.emoji_events, color: Colors.amber, size: 28),
            SizedBox(width: 8),
            Text('Ket qua thi thu'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  const Text('Tong diem uoc tinh', style: TextStyle(color: Colors.grey)),
                  const SizedBox(height: 4),
                  Text(
                    '$tongDiem / 990',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.blueAccent,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Column(
                  children: [
                    const Text('Listening', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('$diemListening / 495', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                  ],
                ),
                Column(
                  children: [
                    const Text('Reading', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('$diemReading / 495', style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
            const Divider(height: 24),
            Text('So cau dung: $soCauDung / ${duLieuCauHoiThiThu.length} cau'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                dangLamBai = false; // Tro ve danh sach de thi
              });
            },
            child: const Text('Hoan thanh & Tro ve'),
          ),
        ],
      ),
    );
  }

  /// Dinh dang giay thanh chuoi mm:ss (Vi du: 1799 giay -> 29:59)
  String dinhDangThoiGian(int tongGiay) {
    int phut = tongGiay ~/ 60;
    int giay = tongGiay % 60;
    return '${phut.toString().padLeft(2, '0')}:${giay.toString().padLeft(2, '0')}';
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
    // GIAO DIEN 1: DANH SACH CAC DE THI THU TOEIC (dangLamBai == false)
    if (!dangLamBai) {
      return Scaffold(
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              'Danh sach de thi thu TOEIC',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              'Luyen tap voi de thi format chuan moi nhat de danh gia dung nang luc.',
              style: TextStyle(color: Colors.grey[600], fontSize: 13),
            ),
            const SizedBox(height: 16),

            _xayDungTheDeThi(
              tenDe: 'ETS TOEIC 2024 - Test 01',
              thoiGian: '120 phut (Full Test)',
              soCau: '200 cau',
              doKho: 'Trung binh (Target 650)',
              khiBamVao: () => batDauThiThu('ETS TOEIC 2024 - Test 01', 30),
            ),
            _xayDungTheDeThi(
              tenDe: 'ETS TOEIC 2024 - Test 02',
              thoiGian: '120 phut (Full Test)',
              soCau: '200 cau',
              doKho: 'Nang cao (Target 800+)',
              khiBamVao: () => batDauThiThu('ETS TOEIC 2024 - Test 02', 30),
            ),
            _xayDungTheDeThi(
              tenDe: 'Mini Test TOEIC - 30 Phut',
              thoiGian: '30 phut (Rut gon)',
              soCau: '20 cau chon loc',
              doKho: 'Co ban (Target 500)',
              khiBamVao: () => batDauThiThu('Mini Test TOEIC - 30 Phut', 15),
            ),
            _xayDungTheDeThi(
              tenDe: 'Chuyen de Reading Part 5 & 6',
              thoiGian: '45 phut',
              soCau: '46 cau',
              doKho: 'Luyen phan xa ngu phap',
              khiBamVao: () => batDauThiThu('Chuyen de Reading Part 5 & 6', 20),
            ),
          ],
        ),
      );
    }

    // GIAO DIEN 2: PHONG LAM BAI THI THU CO TINH GIO (dangLamBai == true)
    final cauHoi = duLieuCauHoiThiThu[cauHienTai];
    final dapAnHienTai = danhSachDapAnDaChon[cauHienTai];
    final coDanhDau = danhSachDanhDau[cauHienTai];

    return Scaffold(
      // WIDGET: AppBar
      // Hien thi ten de thi va dong ho dem nguoc thoi gian real-time
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(tenDeThiHienTai, style: const TextStyle(fontSize: 14)),
            Text(
              'Con lai: ${dinhDangThoiGian(thoiGianConLai)}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: thoiGianConLai < 300 ? Colors.red : Colors.green[700], // Duoi 5 phut doi sang chu do canh bao
              ),
            ),
          ],
        ),
        actions: [
          // Nut tam dung thoi gian
          IconButton(
            icon: Icon(dangTamDung ? Icons.play_arrow : Icons.pause),
            tooltip: dangTamDung ? 'Tiep tuc' : 'Tam dung',
            onPressed: tamDungHoacTiepTuc,
          ),
          // Nut Nop bai tren AppBar
          TextButton(
            onPressed: () => xacNhanNopBai(),
            child: const Text('NOP BAI', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Column(
        children: [
          // WIDGET: Container & ListView.builder (Thanh so thu tu cau hoi 1..20 kieu luoi cuon ngang)
          // Vai tro: Cho phep thi sinh luot nhanh toan bo 20 cau de kiem tra cau nao da lam, cau nao chua lam.
          Container(
            height: 56,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            color: Colors.grey[100],
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: 20,
              itemBuilder: (context, index) {
                final daLam = danhSachDapAnDaChon[index] != -1;
                final dangChon = index == cauHienTai;
                final coFlag = danhSachDanhDau[index];

                Color mauNen = Colors.white;
                if (dangChon) {
                  mauNen = Colors.blueAccent;      // Cau dang xem: Mau xanh duong
                } else if (coFlag) {
                  mauNen = Colors.orangeAccent;    // Cau danh dau Flag: Mau cam
                } else if (daLam) {
                  mauNen = Colors.green[100]!;     // Cau da chon dap an: Mau xanh nhe
                }

                // WIDGET: GestureDetector
                // Bat su kien khi bam vao o so cau hoi de nhay den cau do
                return GestureDetector(
                  onTap: () => chonCauHoi(index),
                  child: Container(
                    width: 40,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      color: mauNen,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: dangChon ? Colors.blueAccent : Colors.grey[300]!,
                        width: 1.5,
                      ),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: dangChon ? Colors.white : Colors.black87,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // WIDGET: Expanded & SingleChildScrollView
          // Khu vuc de bai va 4 lua chon A B C D chiem toan bo dien tich con lai
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Chip(label: Text(cauHoi['phan'])),
                      // Nut dat co danh dau Flag xem lai
                      OutlinedButton.icon(
                        onPressed: danhDauXemLai,
                        icon: Icon(
                          coDanhDau ? Icons.flag : Icons.flag_outlined,
                          color: coDanhDau ? Colors.orange : Colors.grey,
                        ),
                        label: Text(
                          coDanhDau ? 'Da danh dau' : 'Danh dau',
                          style: TextStyle(color: coDanhDau ? Colors.orange : Colors.grey),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  Card(
                    elevation: 1,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        cauHoi['noiDung'],
                        style: const TextStyle(fontSize: 16, height: 1.4, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // 4 Lua chon dap an A B C D
                  ...List.generate(4, (index) {
                    final luaChon = cauHoi['cacLuaChon'][index];
                    final duocChon = dapAnHienTai == index;

                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: InkWell(
                        onTap: () => chonDapAn(index),
                        borderRadius: BorderRadius.circular(8),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                          decoration: BoxDecoration(
                            color: duocChon ? Colors.blue[50] : Colors.white,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: duocChon ? Colors.blueAccent : Colors.grey[300]!,
                              width: 1.5,
                            ),
                          ),
                          child: Text(
                            luaChon,
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: duocChon ? FontWeight.bold : FontWeight.normal,
                            ),
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),

          // Thanh cong cu o day: Chuyen cau truoc / sau hoac Nop bai
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(top: BorderSide(color: Colors.grey[200]!)),
            ),
            child: Row(
              children: [
                if (cauHienTai > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => chonCauHoi(cauHienTai - 1),
                      child: const Text('Cau truoc'),
                    ),
                  ),
                if (cauHienTai > 0) const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      if (cauHienTai < 19) {
                        chonCauHoi(cauHienTai + 1);
                      } else {
                        xacNhanNopBai();
                      }
                    },
                    child: Text(cauHienTai < 19 ? 'Cau tiep theo' : 'Nop bai'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// HELPER WIDGET: _xayDungTheDeThi()
  Widget _xayDungTheDeThi({
    required String tenDe,
    required String thoiGian,
    required String soCau,
    required String doKho,
    required VoidCallback khiBamVao,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(tenDe, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(Icons.timer_outlined, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(thoiGian, style: TextStyle(color: Colors.grey[600], fontSize: 13)),
                const SizedBox(width: 12),
                Icon(Icons.help_outline, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(soCau, style: TextStyle(color: Colors.grey[600], fontSize: 13)),
              ],
            ),
            const SizedBox(height: 6),
            Text('Do kho: $doKho', style: const TextStyle(fontSize: 12, color: Colors.blueAccent)),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: khiBamVao,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Vao lam bai thi'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
