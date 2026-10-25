import 'package:flutter/material.dart';

/// MAN HINH: SoTayOnTapManHinh
/// Ke thua StatefulWidget vi can quan ly danh sach cac cau hoi sai cua hoc vien:
/// - boLocPhanThi: Loc danh sach theo tung Part (Tat ca, Part 5, Part 7)
/// - danhSachCauSai: Danh sach du lieu cac cau sai co the xoa bo khi hoc vien da hieu
class SoTayOnTapManHinh extends StatefulWidget {
  const SoTayOnTapManHinh({super.key});

  @override
  State<SoTayOnTapManHinh> createState() => _SoTayOnTapManHinhState();
}

class _SoTayOnTapManHinhState extends State<SoTayOnTapManHinh> {
  // BIEN TRANG THAI (STATE):
  String boLocPhanThi = 'Tat ca';

  // Danh sach cac cau sai mau
  List<Map<String, dynamic>> danhSachCauSai = [
    {
      'id': 1,
      'phan': 'Part 5',
      'cauHoi': 'The CEO announced that bonuses would be distributed _____ the sales targets were met.',
      'cacDapAn': ['A. unless', 'B. provided that', 'C. although', 'D. despite'],
      'dapAnDung': 1,
      'dapAnDaChonSai': 'A. unless',
      'giaiThich': '"Provided that" mang nghia la "mien la / voi dieu kien la". Cau co nghia la tien thuong se duoc phat mien la dat duoc chi tieu ban hang.',
    },
    {
      'id': 2,
      'phan': 'Part 5',
      'cauHoi': 'Neither the director nor his assistants _____ available for an interview today.',
      'cacDapAn': ['A. is', 'B. are', 'C. was', 'D. being'],
      'dapAnDung': 1,
      'dapAnDaChonSai': 'A. is',
      'giaiThich': 'Cau truc "Neither S1 nor S2 + V" thi dong tu chia theo chu ngu thu 2 (S2 = assistants la so nhieu nen dung "are").',
    },
    {
      'id': 3,
      'phan': 'Part 7',
      'cauHoi': 'What is suggested about the new software update mentioned in the memo?',
      'cacDapAn': ['A. It requires additional training', 'B. It is completely free', 'C. It was released yesterday', 'D. It will replace email'],
      'dapAnDung': 0,
      'dapAnDaChonSai': 'B. It is completely free',
      'giaiThich': 'Trong van ban: "Staff are scheduled for workshops on the new system" tuong duong voi "requires additional training".',
    },
  ];

  /// HAM XU LY: locPhanThi()
  /// Hoat dong: Cap nhat tieu chi loc khi hoc vien bam vao cac FilterChip tren thanh cong cu.
  void locPhanThi(String phanMoi) {
    setState(() {
      boLocPhanThi = phanMoi;
    });
  }

  /// HAM XU LY: xoaCauHoiKhoiSoTay()
  /// Hoat dong: Xoa cau hoi ra khoi danh sach khi hoc vien da thuc su hieu ro bai.
  void xoaCauHoiKhoiSoTay(int idCauHoi) {
    setState(() {
      danhSachCauSai.removeWhere((item) => item['id'] == idCauHoi);
    });
    hienThongBao('Tuyet voi! Da xoa cau hoi khoi so tay cau sai.');
  }

  /// HAM XU LY: moHopThoaiLamLai()
  /// WIDGET: showModalBottomSheet & StatefulBuilder
  /// Hoat dong: Mo mot bang dieu khien truot tu duoi day man hinh len tren (Bottom Sheet).
  /// Cho phep nguoi dung thu chon lai dap an ma khong can phai chuyen man hinh khac.
  void moHopThoaiLamLai(Map<String, dynamic> cauHoi) {
    int dapAnChonLai = -1;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Lam lai: ${cauHoi['phan']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                cauHoi['cauHoi'],
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
              // 4 Nut chon lai dap an
              ...List.generate(4, (index) {
                final dapAnText = cauHoi['cacDapAn'][index];
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      backgroundColor: dapAnChonLai == index ? Colors.blue[50] : null,
                      side: BorderSide(color: dapAnChonLai == index ? Colors.blueAccent : Colors.grey[300]!),
                      alignment: Alignment.centerLeft,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onPressed: () {
                      setModalState(() {
                        dapAnChonLai = index;
                      });
                    },
                    child: Text(dapAnText, style: const TextStyle(fontSize: 14)),
                  ),
                );
              }),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  if (dapAnChonLai == -1) {
                    hienThongBao('Vui long chon dap an!');
                    return;
                  }
                  Navigator.pop(context);
                  if (dapAnChonLai == cauHoi['dapAnDung']) {
                    hienThongBao('Chinh xac! Ban da lam dung cau nay.');
                  } else {
                    hienThongBao('Van chua dung, hay doc ky lai giai thich nhe!');
                  }
                },
                child: const Text('Kiem tra ket qua'),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }

  /// HAM XU LY: xemGiaiThichChiTiet()
  /// WIDGET: showDialog & AlertDialog
  /// Hoat dong: Mo hop thoai phan tich ro vi sao dap an do dung va bay thuong gap cua cau hoi.
  void xemGiaiThichChiTiet(Map<String, dynamic> cauHoi) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Giai thich chi tiet'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Cau hoi: ${cauHoi['cauHoi']}', style: const TextStyle(fontWeight: FontWeight.w500)),
            const Divider(height: 16),
            Text('Dap an dung: ${cauHoi['cacDapAn'][cauHoi['dapAnDung']]}', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
            Text('Dap an ban tung chon sai: ${cauHoi['dapAnDaChonSai']}', style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 8),
            Text(cauHoi['giaiThich'], style: const TextStyle(fontSize: 13, height: 1.4)),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Da hieu'),
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
    // Loc danh sach theo Part
    final danhSachHienThi = boLocPhanThi == 'Tat ca'
        ? danhSachCauSai
        : danhSachCauSai.where((c) => c['phan'] == boLocPhanThi).toList();

    // WIDGET: Scaffold
    return Scaffold(
      // WIDGET: AppBar
      appBar: AppBar(
        title: const Text('So tay cau sai'),
      ),
      body: Column(
        children: [
          // WIDGET: FilterChip
          // Vai tro: Cac the chip loc danh sach cho phep click de chon loc theo phan thi
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['Tat ca', 'Part 5', 'Part 7'].map((phan) {
                final duocChon = boLocPhanThi == phan;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(phan),
                    selected: duocChon,
                    onSelected: (bool selected) => locPhanThi(phan),
                  ),
                );
              }).toList(),
            ),
          ),

          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Con ${danhSachHienThi.length} cau can on tap',
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.redAccent),
                ),
                TextButton(
                  onPressed: () {
                    hienThongBao('Che do on tap tat ca cau sai dang duoc chuan bi!');
                  },
                  child: const Text('On tap tat ca'),
                ),
              ],
            ),
          ),

          // WIDGET: Expanded & ListView.builder
          // Danh sach cac the cau sai
          Expanded(
            child: danhSachHienThi.isEmpty
                // Hien thi trang thai trong (Empty State) khi da giai quyet het cau sai
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                        SizedBox(height: 12),
                        Text(
                          'Ban khong co cau sai nao o phan nay!',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 4),
                        Text('Hay tiep tuc duy tri phong do nhe.', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: danhSachHienThi.length,
                    itemBuilder: (context, index) {
                      final item = danhSachHienThi[index];
                      // WIDGET: Card
                      // The Card chua thong tin chi tiet cau hoi sai va 2 nut Xem giai thich / Lam lai
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  // Nhan Part mau do nhe
                                  Chip(
                                    label: Text(item['phan']),
                                    backgroundColor: Colors.red[50],
                                    labelStyle: const TextStyle(color: Colors.redAccent, fontSize: 12),
                                  ),
                                  // Nut xoa cau hoi khoi so tay
                                  IconButton(
                                    icon: const Icon(Icons.delete_outline, color: Colors.grey),
                                    tooltip: 'Da hieu - Xoa khoi so tay',
                                    onPressed: () => xoaCauHoiKhoiSoTay(item['id']),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                item['cauHoi'],
                                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Dap an dung: ${item['cacDapAn'][item['dapAnDung']]}',
                                style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  Expanded(
                                    child: OutlinedButton(
                                      onPressed: () => xemGiaiThichChiTiet(item),
                                      child: const Text('Xem giai thich'),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: ElevatedButton(
                                      onPressed: () => moHopThoaiLamLai(item),
                                      child: const Text('Lam lai'),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
