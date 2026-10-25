import 'package:flutter/material.dart';

/// MAN HINH: LuyenTapManHinh
/// Ke thua StatefulWidget vi can quan ly cac trang thai dong:
/// - partDangChon: Part TOEIC nguoi hoc chon de luyen (1 den 7)
/// - chiSoCauHienTai: Vi tri cau hoi hien tai dang lam
/// - dapAnDaChon: Dap an nguoi dung vua tich chon (0: A, 1: B, 2: C, 3: D, -1: chua chon)
/// - daKiemTra: Da bam nut kiem tra dung/sai de hien thi giai thich chua
class LuyenTapManHinh extends StatefulWidget {
  const LuyenTapManHinh({super.key});

  @override
  State<LuyenTapManHinh> createState() => _LuyenTapManHinhState();
}

class _LuyenTapManHinhState extends State<LuyenTapManHinh> {
  // BIEN TRANG THAI (STATE):
  int partDangChon = 5;       // Mac dinh luyen tap Part 5 (Hoan thanh cau)
  int chiSoCauHienTai = 0;    // Chi so cau hoi bat dau tu 0
  int dapAnDaChon = -1;       // -1 nghia la chua co dap an nao duoc chon
  bool daKiemTra = false;     // true khi da nhan nut Kiem tra

  // Du lieu cau hoi mau cho phan luyen tap
  final List<Map<String, dynamic>> danhSachCauHoi = [
    {
      'cauHoi': 'Ms. Gomez requested that the quarterly financial report be submitted _____ Friday afternoon.',
      'cacDapAn': ['A. on', 'B. by', 'C. in', 'D. at'],
      'dapAnDung': 1, // B. by
      'giaiThich': 'Giai thich: Dung "by + thoi diem" de chi han chot (deadline - truoc hoac muon nhat vao chieu thu Sau).',
      'loaiTu': 'Ngu phap: Gioi tu chi thoi gian',
    },
    {
      'cauHoi': 'The marketing team proposed a _____ new campaign to attract younger consumers.',
      'cacDapAn': ['A. bold', 'B. boldly', 'C. boldness', 'D. baldest'],
      'dapAnDung': 0, // A. bold
      'giaiThich': 'Giai thich: Can mot tinh tu (bold) de bo nghia cho cum danh tu "new campaign".',
      'loaiTu': 'Tu loai: Tinh tu bo nghia danh tu',
    },
    {
      'cauHoi': 'All employees are encouraged to participate in the upcoming safety _____ next week.',
      'cacDapAn': ['A. train', 'B. trainer', 'C. training', 'D. trained'],
      'dapAnDung': 2, // C. training
      'giaiThich': 'Giai thich: "safety training" la cum danh tu ghep co nghia la buoi dao tao an toan.',
      'loaiTu': 'Tu vung: Cum danh tu ghep',
    },
    {
      'cauHoi': 'Despite the severe weather conditions, the flight arrived _____ schedule.',
      'cacDapAn': ['A. on', 'B. in', 'C. of', 'D. for'],
      'dapAnDung': 0, // A. on
      'giaiThich': 'Giai thich: Cum tu co dinh "on schedule" co nghia la dung gio theo lich trinh.',
      'loaiTu': 'Cum tu co dinh (Collocation)',
    },
    {
      'cauHoi': 'Customers who wish to return merchandise must present the original purchase _____.',
      'cacDapAn': ['A. recipient', 'B. recipe', 'C. reception', 'D. receipt'],
      'dapAnDung': 3, // D. receipt
      'giaiThich': 'Giai thich: "receipt" la hoa don mua hang. "recipient" la nguoi nhan, "recipe" la cong thuc nau an.',
      'loaiTu': 'Tu vung: Danh tu kinh doanh',
    },
  ];

  /// HAM XU LY: chonPartLuyenTap()
  /// Hoat dong: Nguoi dung chon Part 1 den 7, he thong dat lai chi so cau ve 0 va lam moi lua chon dap an.
  void chonPartLuyenTap(int partMoi) {
    setState(() {
      partDangChon = partMoi;
      chiSoCauHienTai = 0;
      dapAnDaChon = -1;
      daKiemTra = false;
    });
    hienThongBao('Da chuyen sang luyen tap Part $partMoi');
  }

  /// HAM XU LY: chonDapAn()
  /// Hoat dong: Luu dap an A, B, C, D nguoi dung click chon.
  /// Neu da kiem tra roi thi khoa khong cho doi dap an nua.
  void chonDapAn(int viTriDapAn) {
    if (daKiemTra) return;
    setState(() {
      dapAnDaChon = viTriDapAn;
    });
  }

  /// HAM XU LY: kiemTraDapAn()
  /// Hoat dong: Kich hoat hien thi dung/sai va khung giai thich chi tiet dap an.
  void kiemTraDapAn() {
    if (dapAnDaChon == -1) {
      hienThongBao('Vui long chon 1 dap an truoc khi kiem tra!');
      return;
    }
    setState(() {
      daKiemTra = true;
    });
  }

  /// HAM XU LY: chuyenCauTiepTheo()
  /// Hoat dong: Chuyen sang cau hoi ke tiep, reset lua chon dap an ve -1 va daKiemTra ve false.
  void chuyenCauTiepTheo() {
    if (chiSoCauHienTai < danhSachCauHoi.length - 1) {
      setState(() {
        chiSoCauHienTai += 1;
        dapAnDaChon = -1;
        daKiemTra = false;
      });
    } else {
      hienThongBao('Ban da hoan thanh het cac cau hoi cua phan nay!');
    }
  }

  /// HAM XU LY: chuyenCauTruoc()
  /// Hoat dong: Quay tro lai cau hoi truoc do trong danh sach.
  void chuyenCauTruoc() {
    if (chiSoCauHienTai > 0) {
      setState(() {
        chiSoCauHienTai -= 1;
        dapAnDaChon = -1;
        daKiemTra = false;
      });
    }
  }

  /// HAM XU LY: luuVaoSoTay()
  /// Hoat dong: Luu cau hoi vao So tay de on lai sau nay.
  void luuVaoSoTay() {
    hienThongBao('Da luu cau hoi so ${chiSoCauHienTai + 1} vao So tay cau sai!');
  }

  /// HAM XU LY: lamLaiCauHoi()
  /// Hoat dong: Xoa ket qua kiem tra cua cau hien tai de nguoi dung chon lai tu dau.
  void lamLaiCauHoi() {
    setState(() {
      dapAnDaChon = -1;
      daKiemTra = false;
    });
  }

  /// HAM TIEN ICH: hienThongBao()
  /// WIDGET: SnackBar & ScaffoldMessenger
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
    final cauHienTai = danhSachCauHoi[chiSoCauHienTai];
    final laCauDung = daKiemTra && dapAnDaChon == cauHienTai['dapAnDung'];

    // WIDGET: Scaffold
    // Khung giao dien co ban cua man hinh luyen tap
    return Scaffold(
      // WIDGET: SingleChildScrollView
      // Giup man hinh co the cuon xuong de xem het 4 lua chon A B C D va khung giai thich dap an
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // WIDGET: SizedBox & ListView.builder (Chon Part 1 den 7 kieu cuon ngang)
            // scrollDirection: Axis.horizontal giup danh sach chip Part 1 -> Part 7 cuon muot theo chieu ngang.
            SizedBox(
              height: 44,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: 7,
                itemBuilder: (context, index) {
                  final partNumber = index + 1;
                  final duocChon = partNumber == partDangChon;

                  // WIDGET: ChoiceChip
                  // Vai tro: The chip chon lua kieu nut vien thuoc.
                  // selected: true thi to mau xanh (selectedColor: Colors.blueAccent).
                  // onSelected: Goi ham chonPartLuyenTap khi nguoi dung nhan vao.
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text('Part $partNumber'),
                      selected: duocChon,
                      selectedColor: Colors.blueAccent,
                      labelStyle: TextStyle(
                        color: duocChon ? Colors.white : Colors.black87,
                        fontWeight: FontWeight.bold,
                      ),
                      onSelected: (bool selected) {
                        if (selected) chonPartLuyenTap(partNumber);
                      },
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 16),

            // WIDGET: Row
            // Hien thi tieu de ten Part va tien do cau hoi (Vi du: Cau 1/5)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Part $partDangChon: Hoan thanh cau',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                Text(
                  'Cau ${chiSoCauHienTai + 1}/${danhSachCauHoi.length}',
                  style: TextStyle(color: Colors.blueAccent[700], fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // WIDGET: LinearProgressIndicator
            // Vai tro: Thanh ngang the hien truc quan tien trinh lam bai (Vi du: 2/5 thi thanh lap day 40%).
            LinearProgressIndicator(
              value: (chiSoCauHienTai + 1) / danhSachCauHoi.length,
              backgroundColor: Colors.grey[200],
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.blueAccent),
            ),

            const SizedBox(height: 16),

            // WIDGET: Card
            // The chua noi dung de bai cau hoi TOEIC va tag chu de ngu phap
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // WIDGET: Chip
                        // Nhan the loai ngu phap / tu loai cua cau hoi
                        Chip(
                          label: Text(cauHienTai['loaiTu'], style: const TextStyle(fontSize: 11)),
                          backgroundColor: Colors.blue[50],
                        ),
                        // Nut danh dau luu cau hoi vao So tay
                        IconButton(
                          icon: const Icon(Icons.bookmark_add_outlined, color: Colors.blueAccent),
                          tooltip: 'Luu vao so tay',
                          onPressed: luuVaoSoTay,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // WIDGET: Text
                    // Hien thi cau hoi tieng Anh
                    Text(
                      cauHienTai['cauHoi'],
                      style: const TextStyle(fontSize: 17, height: 1.4, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // WIDGET: List.generate ket hop InkWell & Container
            // Vai tro: Sinh ra 4 lua chon A, B, C, D.
            // Khi chua kiem tra: Dap an duoc chon se doi vien sang mau xanh duong (blueAccent).
            // Khi da kiem tra: Dap an dung doi sang mau xanh la cay (green); dap an nguoi dung chon sai se doi sang mau do (red).
            ...List.generate(4, (index) {
              final dapAnText = cauHienTai['cacDapAn'][index];
              Color mauVien = Colors.grey[300]!;
              Color mauNen = Colors.white;

              if (daKiemTra) {
                if (index == cauHienTai['dapAnDung']) {
                  mauNen = Colors.green[50]!;
                  mauVien = Colors.green;
                } else if (index == dapAnDaChon) {
                  mauNen = Colors.red[50]!;
                  mauVien = Colors.red;
                }
              } else if (dapAnDaChon == index) {
                mauNen = Colors.blue[50]!;
                mauVien = Colors.blueAccent;
              }

              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 6.0),
                // WIDGET: InkWell
                // Cho phep bat su kien click vao dap an va tao hieu ung gorn song
                child: InkWell(
                  onTap: () => chonDapAn(index),
                  borderRadius: BorderRadius.circular(10),
                  // WIDGET: Container
                  // Tao khung o vuong bo goc vien mau cho tung dap an
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: mauNen,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: mauVien, width: 1.5),
                    ),
                    child: Row(
                      children: [
                        Text(
                          dapAnText,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: dapAnDaChon == index ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        const Spacer(), // Day bieu tuong icon check ve sat le phai
                        if (daKiemTra && index == cauHienTai['dapAnDung'])
                          const Icon(Icons.check_circle, color: Colors.green)
                        else if (daKiemTra && index == dapAnDaChon)
                          const Icon(Icons.cancel, color: Colors.red),
                      ],
                    ),
                  ),
                ),
              );
            }),

            const SizedBox(height: 16),

            // KHUNG GIAI THICH CHI TIET (Chi hien thi khi daKiemTra == true)
            if (daKiemTra) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: laCauDung ? Colors.green[50] : Colors.amber[50],
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: laCauDung ? Colors.green : Colors.amber),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          laCauDung ? Icons.check_circle_outline : Icons.info_outline,
                          color: laCauDung ? Colors.green : Colors.amber[800],
                        ),
                        const SizedBox(width: 8),
                        Text(
                          laCauDung ? 'Chinh xac!' : 'Chua dung!',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: laCauDung ? Colors.green[800] : Colors.amber[900],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      cauHienTai['giaiThich'],
                      style: const TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // HANG CAC NUT HANH DONG: Cau truoc - Kiem tra - Cau tiep theo
            Row(
              children: [
                if (chiSoCauHienTai > 0)
                  // WIDGET: OutlinedButton
                  // Nut vien bo ngoai cho hanh dong quay lai cau truoc
                  Expanded(
                    child: OutlinedButton(
                      onPressed: chuyenCauTruoc,
                      child: const Text('Cau truoc'),
                    ),
                  ),
                if (chiSoCauHienTai > 0) const SizedBox(width: 8),

                if (!daKiemTra)
                  // WIDGET: ElevatedButton (Nut Kiem tra dap an)
                  // WIDGET: Expanded
                  // flex: 2 giup nut nay chiem ty le chieu rong lon gap doi nut "Cau truoc"
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: kiemTraDapAn,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blueAccent,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('KIEM TRA DAP AN', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  )
                else ...[
                  // Nut Lam lai
                  Expanded(
                    child: OutlinedButton(
                      onPressed: lamLaiCauHoi,
                      child: const Text('Lam lai'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Nut Cau tiep theo (mau xanh la)
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: chuyenCauTiepTheo,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('CAU TIEP THEO', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}
