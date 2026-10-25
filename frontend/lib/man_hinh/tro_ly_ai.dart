import 'package:flutter/material.dart';

/// MAN HINH: TroLyAiManHinh
/// Ke thua StatefulWidget vi can quan ly hoi thoai chat thoi gian thuc:
/// - danhSachTinNhan: Luu tru cac tin nhan qua lai giua hoc vien va gia su AI
/// - ScrollController: Tu dong cuon tin nhan moi xuong duoi cung
/// - TextEditingController: Doc chuoi nguoi dung go vao o chat
class TroLyAiManHinh extends StatefulWidget {
  const TroLyAiManHinh({super.key});

  @override
  State<TroLyAiManHinh> createState() => _TroLyAiManHinhState();
}

class _TroLyAiManHinhState extends State<TroLyAiManHinh> {
  final TextEditingController oNhapTinNhanController = TextEditingController();
  final ScrollController boCuonTinNhan = ScrollController();

  // Danh sach cac tin nhan giua Nguoi dung va AI
  List<Map<String, dynamic>> danhSachTinNhan = [
    {
      'laAI': true,
      'noiDung': 'Xin chao! Toi la tro ly AI cua GetGoals TOEIC. Toi co the giup ban giai thich dap an, phan tich ngu phap hoac chia se meo thi TOEIC. Ban can ho tro gi hom nay?',
      'thoiGian': 'Vua xong',
    },
  ];

  // Cac cau goi y nhanh nguoi dung co the bam vao hoi ngay
  final List<String> danhSachGoiY = [
    'Meo lam Part 5 TOEIC nhanh?',
    'Phan biet Another va Other?',
    'Cach nghe bat tu khoa Part 2?',
    'Chien thuat lam bai Part 7 khi sap het gio?',
  ];

  @override
  void dispose() {
    oNhapTinNhanController.dispose();
    boCuonTinNhan.dispose();
    super.dispose();
  }

  /// HAM XU LY: guiTinNhan()
  /// Hoat dong: Them tin nhan cua nguoi dung vao danhSachTinNhan, cuon man hinh xuong cuoi,
  /// va goi phanHoiTuDongAI() sau 600ms de gia lap bot tra loi.
  void guiTinNhan({String? noiDungTuyChon}) {
    String tinNhan = (noiDungTuyChon ?? oNhapTinNhanController.text).trim();
    if (tinNhan.isEmpty) return;

    setState(() {
      danhSachTinNhan.add({
        'laAI': false,
        'noiDung': tinNhan,
        'thoiGian': 'Vua xong',
      });
    });

    if (noiDungTuyChon == null) {
      oNhapTinNhanController.clear();
    }

    cuonXuongCuoi();

    Future.delayed(const Duration(milliseconds: 600), () {
      if (!mounted) return;
      phanHoiTuDongAI(tinNhan);
    });
  }

  /// HAM XU LY: phanHoiTuDongAI()
  /// Hoat dong: Phan tich tu khoa trong cau hoi (Part 5, Part 2, Another/Other,...) de tra ve meo thi phu hop.
  void phanHoiTuDongAI(String cauHoi) {
    String cauTraLoi = 'Toi da nhan duoc cau hoi cua ban. Voi phan nay trong TOEIC, ban nen chu y den tu loai truoc va sau cho trong, dong thoi loai tru nhanh cac dap an sai ve mat ngu phap nhe!';

    if (cauHoi.contains('Part 5')) {
      cauTraLoi = 'Meo Part 5: 1. Nhan dien nhanh cau hoi tu loai (nhin 4 dap an co chung goc tu). 2. Xac dinh chu ngu va vi ngu chinh. 3. Voi cau hoi gioi tu, chu y cum di kem (vi du: on schedule, in advance).';
    } else if (cauHoi.contains('Another') || cauHoi.contains('Other')) {
      cauTraLoi = 'Phan biet Another & Other:\n- "Another + danh tu dem duoc so it" (mot cai khac: another cup of coffee).\n- "Other + danh tu so nhieu / khong dem duoc" (nhung cai khac: other students).\n- "The other": cai/nguoi con lai trong so da biet.';
    } else if (cauHoi.contains('Part 2')) {
      cauTraLoi = 'Meo Part 2 Listening:\n- Luon tap trung vao 3 tu dau tien cua cau hoi (Who, Where, When, Why, How).\n- Bẫy phat am tu dong am/dong nghia thuong la dap an SAI.\n- Cau tra loi gian tiep ("Toi khong biet", "Hay hoi sep") thuong la dap an DUNG!';
    }

    setState(() {
      danhSachTinNhan.add({
        'laAI': true,
        'noiDung': cauTraLoi,
        'thoiGian': 'Vua xong',
      });
    });

    cuonXuongCuoi();
  }

  /// HAM XU LY: chonGoiYCoSan()
  void chonGoiYCoSan(String goiY) {
    guiTinNhan(noiDungTuyChon: goiY);
  }

  /// HAM XU LY: xoaLichSuTroChuyen()
  void xoaLichSuTroChuyen() {
    setState(() {
      danhSachTinNhan = [
        {
          'laAI': true,
          'noiDung': 'Lich su chat da duoc lam moi. Ban can hoi them kien thuc TOEIC nao khong?',
          'thoiGian': 'Vua xong',
        },
      ];
    });
    hienThongBao('Da xoa lich su tro chuyen.');
  }

  /// HAM TIEN ICH: cuonXuongCuoi()
  /// CO CHE: ScrollController.animateTo
  /// Hoat dong: Cuon danh sach xuong vi tri maxScrollExtent voi hieu ung Curves.easeOut em diu trong 250ms.
  void cuonXuongCuoi() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (boCuonTinNhan.hasClients) {
        boCuonTinNhan.animateTo(
          boCuonTinNhan.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
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
    // Khung man hinh chat AI
    return Scaffold(
      // WIDGET: AppBar
      // Thanh tieu de chua avatar bot AI va nut xoa lich su chat
      appBar: AppBar(
        title: const Row(
          children: [
            CircleAvatar(
              backgroundColor: Colors.blueAccent,
              child: Icon(Icons.smart_toy, color: Colors.white, size: 20),
            ),
            SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Tro ly GetGoals AI', style: TextStyle(fontSize: 16)),
                Text('San sang ho tro 24/7', style: TextStyle(fontSize: 11, color: Colors.grey)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep_outlined),
            tooltip: 'Xoa lich su',
            onPressed: xoaLichSuTroChuyen,
          ),
        ],
      ),

      body: Column(
        children: [
          // WIDGET: Expanded & ListView.builder (VUNG DANH SACH TIN NHAN)
          // controller: boCuonTinNhan de dieu khien cuon tu dong
          Expanded(
            child: ListView.builder(
              controller: boCuonTinNhan,
              padding: const EdgeInsets.all(16),
              itemCount: danhSachTinNhan.length,
              itemBuilder: (context, index) {
                final tinNhan = danhSachTinNhan[index];
                final laAI = tinNhan['laAI'] as bool;

                // WIDGET: Align & Container (BONG BONG CHAT)
                // laAI == true: Can le trai (Alignment.centerLeft), mau xam nhe (grey[200])
                // laAI == false: Can le phai (Alignment.centerRight), mau xanh duong (blueAccent)
                return Align(
                  alignment: laAI ? Alignment.centerLeft : Alignment.centerRight,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 6),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    // constraints: Gioi han chieu rong toi da khong vuot qua 78% chieu rong man hinh
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
                    decoration: BoxDecoration(
                      color: laAI ? Colors.grey[200] : Colors.blueAccent,
                      // Bo goc bat doi xung: Tao hinh bong bong chat tin nhan thuc te
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(14),
                        topRight: const Radius.circular(14),
                        bottomLeft: Radius.circular(laAI ? 2 : 14),
                        bottomRight: Radius.circular(laAI ? 14 : 2),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: laAI ? CrossAxisAlignment.start : CrossAxisAlignment.end,
                      children: [
                        Text(
                          tinNhan['noiDung'],
                          style: TextStyle(
                            color: laAI ? Colors.black87 : Colors.white,
                            fontSize: 14,
                            height: 1.4,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          tinNhan['thoiGian'],
                          style: TextStyle(
                            color: laAI ? Colors.grey[600] : Colors.white70,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // WIDGET: SizedBox & ListView.builder (HANG CHIP GOI Y CAU HOI NHANH)
          // Cho phep nguoi dung nhan vao de hoi nhanh cac meo lam de TOEIC
          Container(
            height: 40,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: danhSachGoiY.length,
              itemBuilder: (context, index) {
                final goiY = danhSachGoiY[index];
                // WIDGET: ActionChip
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ActionChip(
                    label: Text(goiY, style: const TextStyle(fontSize: 11)),
                    onPressed: () => chonGoiYCoSan(goiY),
                  ),
                );
              },
            ),
          ),

          const Divider(height: 8),

          // KHUNG NHAP TIN NHAN VA NUT GUI
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
            child: Row(
              children: [
                Expanded(
                  // WIDGET: TextField
                  // O nhap van ban chat voi vien bo tron 24 pixel dang vien thuoc hien dai
                  child: TextField(
                    controller: oNhapTinNhanController,
                    onSubmitted: (val) => guiTinNhan(),
                    decoration: InputDecoration(
                      hintText: 'Hoi AI ve cau hoi, tu vung, meo thi...',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                // WIDGET: CircleAvatar & IconButton
                // Nut icon send gui tin nhan
                CircleAvatar(
                  backgroundColor: Colors.blueAccent,
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white, size: 20),
                    tooltip: 'Gui tin nhan',
                    onPressed: () => guiTinNhan(),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
