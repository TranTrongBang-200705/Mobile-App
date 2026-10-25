import 'package:flutter/material.dart';
import 'kiem_tra_dau_vao.dart';

/// MAN HINH: LoTrinhHocManHinh
/// Ke thua StatefulWidget vi can quan ly:
/// - mucTieuDiem: Muc tieu diem TOEIC cua hoc vien (450, 600, 750, 850, 990)
/// - changDangXem: Chang hoc dang duoc chon xem chi tiet (Chang 1, Chang 2, hoac Chang 3)
/// - danhSachBaiHoc: Trang thai hoan thanh (checkbox) cua cac bai hoc trong chang
class LoTrinhHocManHinh extends StatefulWidget {
  const LoTrinhHocManHinh({super.key});

  @override
  State<LoTrinhHocManHinh> createState() => _LoTrinhHocManHinhState();
}

class _LoTrinhHocManHinhState extends State<LoTrinhHocManHinh> {
  // BIEN TRANG THAI (STATE):
  int mucTieuDiem = 750;
  int changDangXem = 1; // 0: Chang 1, 1: Chang 2, 2: Chang 3

  // Danh sach cac bai hoc trong Chang 2
  List<Map<String, dynamic>> danhSachBaiHoc = [
    {'tieuDe': 'Bai 1: Chuyen de Thi trong tieng Anh & Part 5', 'hoanThanh': true, 'thoiLuong': '25 phut'},
    {'tieuDe': 'Bai 2: Kien thuc Menh de quan he & Dai tu', 'hoanThanh': true, 'thoiLuong': '30 phut'},
    {'tieuDe': 'Bai 3: Chien thuat nghe Part 2: Cau hoi WH-', 'hoanThanh': true, 'thoiLuong': '40 phut'},
    {'tieuDe': 'Bai 4: Ky thuat Skimming & Scanning Part 7', 'hoanThanh': false, 'thoiLuong': '35 phut'},
    {'tieuDe': 'Bai 5: Tu vung chu de Hop dong & Dam phan', 'hoanThanh': false, 'thoiLuong': '20 phut'},
    {'tieuDe': 'Bai 6: Bai kiem tra tien do giua chang 2', 'hoanThanh': false, 'thoiLuong': '60 phut'},
  ];

  /// HAM XU LY: chonChang()
  /// Hoat dong: Nguoi dung bam vao Card cua Chang 1, 2, hoac 3 de xem chi tiet.
  void chonChang(int indexChang) {
    setState(() {
      changDangXem = indexChang;
    });
  }

  /// HAM XU LY: danhDauBaiHoc()
  /// Hoat dong: Tich chon checkbox de cap nhat trang thai hoan thanh bai hoc.
  void danhDauBaiHoc(int indexBai) {
    setState(() {
      danhSachBaiHoc[indexBai]['hoanThanh'] = !danhSachBaiHoc[indexBai]['hoanThanh'];
    });
    final trangThai = danhSachBaiHoc[indexBai]['hoanThanh'];
    hienThongBao(trangThai
        ? 'Da hoan thanh: ${danhSachBaiHoc[indexBai]['tieuDe']}'
        : 'Da bo danh dau hoan thanh.');
  }

  /// HAM XU LY: moHopThoaiDatMucTieu()
  /// WIDGET: showDialog & StatefulBuilder
  /// Hoat dong: StatefulBuilder giup hop thoai co the cap nhat trang thai noi bo (setDialogState)
  /// khi nguoi dung chon Dropdown gia tri moi truoc khi bam Luu.
  void moHopThoaiDatMucTieu() {
    int diemTam = mucTieuDiem;
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Dat muc tieu diem TOEIC'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Chon so diem ban mong muon dat duoc:'),
              const SizedBox(height: 16),
              // WIDGET: DropdownButton
              // Chon muc tieu diem tren thang 990
              DropdownButton<int>(
                isExpanded: true,
                value: diemTam,
                items: const [
                  DropdownMenuItem(value: 450, child: Text('450+ (Tot nghiep co ban)')),
                  DropdownMenuItem(value: 600, child: Text('600+ (Chuan ra truong & di lam)')),
                  DropdownMenuItem(value: 750, child: Text('750+ (Yeu cau doanh nghiep lon)')),
                  DropdownMenuItem(value: 850, child: Text('850+ (Chuyen nghiep & quan ly)')),
                  DropdownMenuItem(value: 990, child: Text('990 (Diem tuyet doi)')),
                ],
                onChanged: (int? giaTriMoi) {
                  if (giaTriMoi != null) {
                    setDialogState(() {
                      diemTam = giaTriMoi;
                    });
                  }
                },
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
                setState(() {
                  mucTieuDiem = diemTam;
                });
                Navigator.pop(context);
                hienThongBao('Da cap nhat muc tieu: $mucTieuDiem TOEIC!');
              },
              child: const Text('Luu muc tieu'),
            ),
          ],
        ),
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
    int soBaiHoanThanh = danhSachBaiHoc.where((b) => b['hoanThanh'] == true).length;
    double phanTram = danhSachBaiHoc.isEmpty ? 0 : soBaiHoanThanh / danhSachBaiHoc.length;

    // WIDGET: Scaffold
    // Khung giao dien co ban
    return Scaffold(
      // WIDGET: AppBar
      appBar: AppBar(
        title: const Text('Lo trinh hoc tap'),
        actions: [
          // Nut lam bai test dau vao de phan loai lai
          IconButton(
            icon: const Icon(Icons.psychology_outlined),
            tooltip: 'Test trinh do dau vao',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const KiemTraDauVaoManHinh()),
              );
            },
          ),
          // Nut mo hop thoai doi muc tieu
          IconButton(
            icon: const Icon(Icons.edit_note),
            tooltip: 'Doi muc tieu',
            onPressed: moHopThoaiDatMucTieu,
          ),
        ],
      ),

      // WIDGET: SingleChildScrollView
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // WIDGET: Container voi LinearGradient
            // Vai tro: Banner tren cung hien thi muc tieu diem voi hieu ung mau gradient chuyen tiep bat mat
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.blueAccent, Colors.indigo], // Chuyen mau tu xanh duong sang xanh tram
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Muc tieu cua ban', style: TextStyle(color: Colors.white70, fontSize: 13)),
                      const SizedBox(height: 4),
                      Text(
                        '$mucTieuDiem+ TOEIC',
                        style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      const Text('Du kien dat duoc: 60 ngay nua', style: TextStyle(color: Colors.white, fontSize: 12)),
                    ],
                  ),
                  ElevatedButton(
                    onPressed: moHopThoaiDatMucTieu,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.indigo,
                    ),
                    child: const Text('Doi muc tieu'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Tieu de danh sach 3 chang hoc
            const Text(
              'Cac chang tren lo trinh',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // WIDGET: _xayDungCardChang
            // 3 Card the hien tien trinh 3 chang hoc tap
            _xayDungCardChang(
              soThuTu: 1,
              tenChang: 'Chang 1: Nen tang vung chac (350 - 450)',
              trangThai: 'Da hoan thanh 100%',
              tienDo: 1.0,
              mauSac: Colors.green,
              duocChon: changDangXem == 0,
              khiBam: () => chonChang(0),
            ),
            _xayDungCardChang(
              soThuTu: 2,
              tenChang: 'Chang 2: But pha ky nang (450 - 650)',
              trangThai: 'Dang hoc (${(phanTram * 100).toInt()}%)',
              tienDo: phanTram,
              mauSac: Colors.orange,
              duocChon: changDangXem == 1,
              khiBam: () => chonChang(1),
            ),
            _xayDungCardChang(
              soThuTu: 3,
              tenChang: 'Chang 3: Chinh phuc dinh cao (650 - 800+)',
              trangThai: 'Sap mo (Can hoan thanh chang 2)',
              tienDo: 0.0,
              mauSac: Colors.grey,
              duocChon: changDangXem == 2,
              khiBam: () => chonChang(2),
            ),

            const SizedBox(height: 20),

            // WIDGET: ListView.builder
            // Danh sach cac bai hoc nam trong chang dang xem chi tiet
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Danh sach bai hoc trong chang',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text('$soBaiHoanThanh/${danhSachBaiHoc.length} bai', style: const TextStyle(color: Colors.blueAccent)),
              ],
            ),
            const SizedBox(height: 8),

            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: danhSachBaiHoc.length,
              itemBuilder: (context, index) {
                final baiHoc = danhSachBaiHoc[index];
                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  // WIDGET: ListTile
                  // Bo cuc chuan gom: leading (Checkbox), title (Ten bai), subtitle (Thoi luong), trailing (Nut Vao hoc)
                  child: ListTile(
                    leading: Checkbox(
                      value: baiHoc['hoanThanh'],
                      onChanged: (bool? giaTri) => danhDauBaiHoc(index),
                    ),
                    title: Text(
                      baiHoc['tieuDe'],
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        decoration: baiHoc['hoanThanh'] ? TextDecoration.lineThrough : null,
                        color: baiHoc['hoanThanh'] ? Colors.grey : Colors.black87,
                      ),
                    ),
                    subtitle: Text('Thoi luong: ${baiHoc['thoiLuong']}'),
                    trailing: ElevatedButton(
                      onPressed: () => hienThongBao('Bat dau hoc: ${baiHoc['tieuDe']}'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: baiHoc['hoanThanh'] ? Colors.grey[300] : Colors.blueAccent,
                        foregroundColor: baiHoc['hoanThanh'] ? Colors.black87 : Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      ),
                      child: Text(baiHoc['hoanThanh'] ? 'Hoc lai' : 'Vao hoc'),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  /// HELPER WIDGET: _xayDungCardChang()
  Widget _xayDungCardChang({
    required int soThuTu,
    required String tenChang,
    required String trangThai,
    required double tienDo,
    required Color mauSac,
    required bool duocChon,
    required VoidCallback khiBam,
  }) {
    return Card(
      elevation: duocChon ? 3 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: duocChon ? Colors.blueAccent : Colors.transparent,
          width: 1.5,
        ),
      ),
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: khiBam,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(tenChang, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  ),
                  Text(trangThai, style: TextStyle(color: mauSac, fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              // WIDGET: LinearProgressIndicator
              // Thanh mau the hien tien do hoan thanh cua tung chang
              LinearProgressIndicator(
                value: tienDo,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(mauSac),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
