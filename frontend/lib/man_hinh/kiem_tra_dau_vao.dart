import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'trang_chu.dart';

/// MAN HINH: KiemTraDauVaoManHinh
/// Tich hop PCAT (Paper-Level Computerized Adaptive Testing) + NCD (Neural Cognitive Diagnosis)
/// Co trinh phat Audio cho cac phan Listening (Part 1 - 4).
class KiemTraDauVaoManHinh extends StatefulWidget {
  const KiemTraDauVaoManHinh({super.key, this.client});

  final http.Client? client;

  @override
  State<KiemTraDauVaoManHinh> createState() => _KiemTraDauVaoManHinhState();
}

class _KiemTraDauVaoManHinhState extends State<KiemTraDauVaoManHinh> {
  static const String baseUrl = String.fromEnvironment(
    'PCAT_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  // Trinh phat Audio
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool dangPhatAudio = false;

  // BIEN TRANG THAI (STATE):
  // 0: Gioi thieu, 1: Dang lam bai, 2: Ket qua
  int trangThaiManHinh = 0;
  bool dangTaiDuLieu = false;
  String? loiTaiDe;
  String? pcatSessionId;

  int changHienTai = 1;
  String tenNhanhChang2 = '';
  String moTaNhanhChang2 = '';

  int thoiGianConLai = 2700;
  Timer? boDemThoiGian;

  List<Map<String, dynamic>> danhSachCauHoiHienTai = [];
  int cauHienTaiTrongChang = 0;
  List<int> dapAnChang1 = [];
  List<int> dapAnChang2 = [];
  List<int> dapAnChonHienTai = [];

  List<Map<String, dynamic>> cauHoiChang1 = [];
  List<Map<String, dynamic>> cauHoiChang2 = [];

  Map<String, dynamic>? ketQuaNCD;
  int soCauDungTong = 0;
  int soCauDungNghe = 0;
  int soCauDungDoc = 0;
  List<dynamic> danhSachKyNangRadar = [];
  List<dynamic> danhSachPartSummary = [];
  List<dynamic> diemManh = [];
  List<dynamic> diemYeu = [];

  @override
  void initState() {
    super.initState();
    _audioPlayer.onPlayerComplete.listen((_) {
      if (mounted) {
        setState(() {
          dangPhatAudio = false;
        });
      }
    });
  }

  @override
  void dispose() {
    boDemThoiGian?.cancel();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> phatHoacDungAudio(String? audioUrl) async {
    if (audioUrl == null || audioUrl.isEmpty) {
      hienThongBao('Không tìm thấy nguồn phát audio cho câu hỏi này.');
      return;
    }

    if (dangPhatAudio) {
      await _audioPlayer.pause();
      setState(() {
        dangPhatAudio = false;
      });
    } else {
      try {
        final resolvedAudioUrl = Uri.parse(baseUrl).resolve(audioUrl).toString();
        await _audioPlayer.play(UrlSource(resolvedAudioUrl));
        setState(() {
          dangPhatAudio = true;
        });
      } catch (e) {
        debugPrint('Loi phat audio: $e');
        hienThongBao('Lỗi kết nối audio đến máy chủ: $e');
      }
    }
  }

  Future<void> dungAudioNeuDangPhat() async {
    if (dangPhatAudio) {
      await _audioPlayer.stop();
      setState(() {
        dangPhatAudio = false;
      });
    }
  }

  Future<void> batDauLamTest() async {
    setState(() {
      dangTaiDuLieu = true;
      loiTaiDe = null;
    });

    try {
      final response = await (widget.client?.get(Uri.parse('$baseUrl/api/pcat/stage1')) ??
              http.get(Uri.parse('$baseUrl/api/pcat/stage1')))
          .timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final List questions = data['questions'];

        setState(() {
          pcatSessionId = data['session_id'] as String?;
          changHienTai = 1;
          cauHoiChang1 = List<Map<String, dynamic>>.from(questions);
          danhSachCauHoiHienTai = cauHoiChang1;
          dapAnChang1 = List.filled(danhSachCauHoiHienTai.length, -1);
          dapAnChonHienTai = dapAnChang1;
          cauHienTaiTrongChang = 0;
          trangThaiManHinh = 1;
          thoiGianConLai = 2700;
          dangTaiDuLieu = false;
        });
        batDauDemGio();
        hienThongBao('Đã tải đề Chặng 1 (Medium - 10 câu). Bấm nút Play để nghe Audio!');
        return;
      }
      if (response.statusCode == 503) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        if (mounted) {
          setState(() {
            dangTaiDuLieu = false;
            loiTaiDe = data['detail']?.toString() ?? 'Bộ đề chưa sẵn sàng.';
          });
        }
        return;
      }
    } catch (e) {
      debugPrint('Loi ket noi backend PCAT: $e');
    }

    if (mounted) {
      setState(() {
        dangTaiDuLieu = false;
        loiTaiDe = 'Không thể tải đề từ máy chủ PCAT. Vui lòng thử lại.';
      });
    }
  }

  void batDauDemGio() {
    boDemThoiGian?.cancel();
    boDemThoiGian = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (thoiGianConLai > 0) {
        setState(() {
          thoiGianConLai--;
        });
      } else {
        timer.cancel();
        xuLyHetGio();
      }
    });
  }

  void chonDapAn(int index) {
    setState(() {
      dapAnChonHienTai[cauHienTaiTrongChang] = index;
    });
  }

  void chuyenCauTiepTheo() {
    dungAudioNeuDangPhat();
    if (cauHienTaiTrongChang < danhSachCauHoiHienTai.length - 1) {
      setState(() {
        cauHienTaiTrongChang++;
      });
    } else {
      xacNhanHoanThanhChang();
    }
  }

  void quayLaiCauTruoc() {
    dungAudioNeuDangPhat();
    if (cauHienTaiTrongChang > 0) {
      setState(() {
        cauHienTaiTrongChang--;
      });
    }
  }

  void xacNhanHoanThanhChang() {
    dungAudioNeuDangPhat();
    int soCauDaLam = dapAnChonHienTai.where((da) => da != -1).length;

    if (changHienTai == 1) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.psychology, color: Colors.blueAccent),
              SizedBox(width: 8),
              Text('Hoàn thành Chặng 1'),
            ],
          ),
          content: Text(
            'Bạn đã làm $soCauDaLam / ${danhSachCauHoiHienTai.length} câu Chặng 1.\n'
            'Hệ thống AI sẽ chẩn đoán năng lực sơ bộ để chọn nhánh đề Chặng 2 (Easy hoặc Hard) phù hợp nhất cho bạn.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Làm tiếp'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                guiChang1VaDinhTuyenChang2();
              },
              child: const Text('AI Phân nhánh Chặng 2'),
            ),
          ],
        ),
      );
    } else {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Nộp toàn bộ 20 câu kiểm tra'),
          content: Text(
            'Bạn đã hoàn thành cả 2 chặng ($soCauDaLam / 10 câu Chặng 2).\n'
            'Nộp bài để xem số câu đúng và các chỉ số NCD trên những kỹ năng đã được khảo sát?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Kiểm tra lại'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                nopBaiToanDienVaChanDoan();
              },
              child: const Text('Nộp bài & Xem Hồ sơ Năng lực'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> guiChang1VaDinhTuyenChang2() async {
    setState(() {
      dangTaiDuLieu = true;
    });

    List<Map<String, dynamic>> payloadAns = [];
    for (int i = 0; i < cauHoiChang1.length; i++) {
      payloadAns.add({
        'q_idx': cauHoiChang1[i]['q_idx'],
        'selected_answer_index': dapAnChang1[i],
      });
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/pcat/route'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'session_id': pcatSessionId,
          'user_id': 'student_getgoals',
          'stage1_answers': payloadAns,
        }),
      ).timeout(const Duration(seconds: 25));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final List questions = data['stage2_questions'];

        setState(() {
          changHienTai = 2;
          tenNhanhChang2 = data['branch_title'] ?? '';
          moTaNhanhChang2 = data['branch_description'] ?? '';
          cauHoiChang2 = List<Map<String, dynamic>>.from(questions);
          danhSachCauHoiHienTai = cauHoiChang2;
          dapAnChang2 = List.filled(danhSachCauHoiHienTai.length, -1);
          dapAnChonHienTai = dapAnChang2;
          cauHienTaiTrongChang = 0;
          dangTaiDuLieu = false;
        });

        if (mounted) {
          showDialog(
            context: context,
            builder: (ctx) => AlertDialog(
              title: Row(
                children: [
                  Icon(
                    data['routed_branch'] == 'hard' ? Icons.trending_up : Icons.assignment_turned_in,
                    color: data['routed_branch'] == 'hard' ? Colors.deepPurple : Colors.teal,
                  ),
                  const SizedBox(width: 8),
                  const Text('AI đã phân nhánh đề thi'),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(tenNhanhChang2, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 8),
                  Text(moTaNhanhChang2),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: Colors.blue[50], borderRadius: BorderRadius.circular(8)),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Số câu đúng Chặng 1:', style: const TextStyle(fontWeight: FontWeight.w500)),
                            Text('${data['stage1_correct_count']}/10 câu (${data['stage1_accuracy_pct']}%)', style: const TextStyle(fontWeight: FontWeight.bold)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('Chỉ số NCD tiềm ẩn:', style: TextStyle(fontWeight: FontWeight.w500)),
                            Text('${(data['stage1_mastery_score'] * 100).toStringAsFixed(1)}% (< ngưỡng 43.4%)', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo)),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              actions: [
                ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Bắt đầu làm Chặng 2'),
                ),
              ],
            ),
          );
        }
        return;
      }
    } catch (e) {
      debugPrint('Loi goi API route: $e');
    }

    if (mounted) {
      setState(() => dangTaiDuLieu = false);
      hienThongBao('Không thể phân nhánh từ máy chủ PCAT. Vui lòng thử lại.');
    }
  }

  Future<void> nopBaiToanDienVaChanDoan() async {
    boDemThoiGian?.cancel();
    dungAudioNeuDangPhat();

    setState(() {
      dangTaiDuLieu = true;
    });

    List<Map<String, dynamic>> payload20 = [];
    for (int i = 0; i < cauHoiChang1.length; i++) {
      payload20.add({
        'q_idx': cauHoiChang1[i]['q_idx'],
        'selected_answer_index': dapAnChang1[i],
      });
    }
    for (int i = 0; i < cauHoiChang2.length; i++) {
      payload20.add({
        'q_idx': cauHoiChang2[i]['q_idx'],
        'selected_answer_index': dapAnChang2[i],
      });
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/pcat/diagnose'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'session_id': pcatSessionId,
          'user_id': 'student_getgoals',
          'all_answers': payload20,
        }),
      ).timeout(const Duration(seconds: 25));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        setState(() {
          ketQuaNCD = data;
          soCauDungTong = data['correct_answers'] ?? 0;
          soCauDungNghe = data['correct_listening'] ?? 0;
          soCauDungDoc = data['correct_reading'] ?? 0;
          danhSachKyNangRadar = data['radar_skills'] ?? [];
          danhSachPartSummary = data['part_summary'] ?? [];
          diemManh = data['strengths'] ?? [];
          diemYeu = data['weaknesses'] ?? [];
          trangThaiManHinh = 2;
          dangTaiDuLieu = false;
        });
        hienThongBao('Đã hoàn thành hồ sơ NCD trên các kỹ năng đã khảo sát.');
        return;
      }
    } catch (e) {
      debugPrint('Loi goi API diagnose: $e');
    }

    if (mounted) {
      setState(() => dangTaiDuLieu = false);
      hienThongBao('Không thể chẩn đoán từ máy chủ PCAT. Vui lòng thử lại.');
    }
  }

  void xuLyHetGio() {
    hienThongBao('Hết thời gian làm bài!');
    if (changHienTai == 1) {
      guiChang1VaDinhTuyenChang2();
    } else {
      nopBaiToanDienVaChanDoan();
    }
  }

  void batDauLoTrinhDeXuat() {
    hienThongBao('Chào mừng bạn đến với lộ trình học cá nhân hóa!');
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const TrangChuManHinh()),
    );
  }

  void lamLaiTest() {
    setState(() {
      pcatSessionId = null;
      trangThaiManHinh = 0;
      changHienTai = 1;
      ketQuaNCD = null;
    });
  }

  String dinhDangThoiGian(int tongGiay) {
    int phut = tongGiay ~/ 60;
    int giay = tongGiay % 60;
    return '${phut.toString().padLeft(2, '0')}:${giay.toString().padLeft(2, '0')}';
  }

  void hienThongBao(String noiDung) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(noiDung),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (dangTaiDuLieu) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(color: Colors.blueAccent),
              const SizedBox(height: 20),
              const Text(
                'AI PCAT & NCD đang phân tích...',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 6),
              Text(
                changHienTai == 1
                    ? 'Đang chuẩn bị đề Chặng 1...'
                    : 'Đang giải mã mạng nơ-ron để định vị nhánh đề & kỹ năng...',
                style: const TextStyle(color: Colors.grey),
              ),
            ],
          ),
        ),
      );
    }

    // ==================== GIAI DOAN 0: MAN GIOI THIEU TEST DAU VAO ====================
    if (trangThaiManHinh == 0) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Đề thi test trình độ'),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Center(
                child: Icon(
                  Icons.psychology_outlined,
                  size: 80,
                  color: Colors.blueAccent,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Đề thi test trình độ',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),

              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: const Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(Icons.alt_route, color: Colors.blueAccent),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Thi thích ứng 2 chặng (Listening & Reading)',
                              style: TextStyle(fontWeight: FontWeight.w600),
                            ),
                          ),
                        ],
                      ),
                      Divider(height: 20),
                      Row(
                        children: [
                          Icon(Icons.headphones, color: Colors.indigo),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text('Tích hợp Audio Listening giọng đọc chuẩn Mỹ / Anh', style: TextStyle(fontWeight: FontWeight.w600)),
                          ),
                        ],
                      ),
                      Divider(height: 20),
                      Row(
                        children: [
                          Icon(Icons.timer_outlined, color: Colors.green),
                          SizedBox(width: 12),
                          Text('Thời gian làm bài: 45 phút', style: TextStyle(fontWeight: FontWeight.w600)),
                        ],
                      ),
                      Divider(height: 20),
                      Row(
                        children: [
                          Icon(Icons.hub, color: Colors.purple),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text('Xuất điểm yếu và điểm mạnh', style: TextStyle(fontWeight: FontWeight.w600)),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 32),

              if (loiTaiDe != null) ...[
                Card(
                  color: Colors.orange[50],
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(loiTaiDe!, style: const TextStyle(color: Colors.deepOrange)),
                  ),
                ),
                const SizedBox(height: 12),
              ],

              ElevatedButton.icon(
                onPressed: batDauLamTest,
                icon: const Icon(Icons.play_arrow),
                label: const Text('BẮT ĐẦU LÀM BÀI TEST THÍCH ỨNG NGAY', style: TextStyle(fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => const TrangChuManHinh()),
                  );
                },
                child: const Text('Để sau, vào thẳng Trang chủ'),
              ),
            ],
          ),
        ),
      );
    }

    // ==================== GIAI DOAN 1: MAN HINH DANG LAM BAI TEST ====================
    if (trangThaiManHinh == 1) {
      final cauHoi = danhSachCauHoiHienTai[cauHienTaiTrongChang];
      final dapAnChon = dapAnChonHienTai[cauHienTaiTrongChang];
      final int cauTongSo = (changHienTai == 1 ? 0 : 10) + cauHienTaiTrongChang + 1;
      final int part = cauHoi['part'] ?? 5;
      final bool isListening = (part <= 4);
      final String? audioUrl = cauHoi['audio_url'];

      return Scaffold(
        appBar: AppBar(
          title: Text(
            changHienTai == 1
                ? 'Chặng 1: Câu $cauTongSo/20'
                : 'Chặng 2: Câu $cauTongSo/20',
            style: const TextStyle(fontSize: 16),
          ),
          actions: [
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 16),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: thoiGianConLai < 180 ? Colors.red[50] : Colors.blue[50],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.timer, size: 16, color: thoiGianConLai < 180 ? Colors.red : Colors.blueAccent),
                      const SizedBox(width: 4),
                      Text(
                        dinhDangThoiGian(thoiGianConLai),
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: thoiGianConLai < 180 ? Colors.red : Colors.blueAccent,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
        body: Column(
          children: [
            LinearProgressIndicator(
              value: cauTongSo / 20.0,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                changHienTai == 1 ? Colors.blueAccent : Colors.deepPurple,
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Thanh danh sách điều hướng nhanh các câu: Câu 1, Câu 2, ...
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: List.generate(danhSachCauHoiHienTai.length, (i) {
                          final int soCau = changHienTai == 1 ? (i + 1) : (i + 11);
                          final bool dangChon = i == cauHienTaiTrongChang;
                          final bool daLam = dapAnChonHienTai[i] != -1;

                          return Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: InkWell(
                              onTap: () {
                                setState(() {
                                  cauHienTaiTrongChang = i;
                                });
                              },
                              borderRadius: BorderRadius.circular(20),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                                decoration: BoxDecoration(
                                  color: dangChon
                                      ? (changHienTai == 1 ? Colors.blueAccent : Colors.deepPurple)
                                      : (daLam ? Colors.blue[50] : Colors.grey[100]),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: dangChon
                                        ? (changHienTai == 1 ? Colors.blueAccent : Colors.deepPurple)
                                        : (daLam ? Colors.blueAccent.withValues(alpha: 0.5) : Colors.grey[300]!),
                                    width: dangChon ? 2 : 1,
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    if (daLam && !dangChon) ...[
                                      const Icon(Icons.check_circle, size: 14, color: Colors.blueAccent),
                                      const SizedBox(width: 4),
                                    ],
                                    Text(
                                      'Câu $soCau',
                                      style: TextStyle(
                                        color: dangChon ? Colors.white : Colors.black87,
                                        fontWeight: dangChon ? FontWeight.bold : FontWeight.w500,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        }),
                      ),
                    ),
                    const SizedBox(height: 12),

                    if (part == 1 && cauHoi['image_url'] != null) ...[
                      Image.network(
                        Uri.parse(baseUrl).resolve(cauHoi['image_url'].toString()).toString(),
                        height: 220,
                        fit: BoxFit.contain,
                        errorBuilder: (_, error, stackTrace) =>
                            const Text('Không tải được ảnh cho câu hỏi này.'),
                      ),
                      const SizedBox(height: 12),
                    ],

                    // ================= KHUNG AUDIO PLAYER CHO PHAN LISTENING =================
                    if (isListening) ...[
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.blue[50]!, Colors.indigo[50]!],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
                        ),
                        child: Row(
                          children: [
                            IconButton(
                              iconSize: 44,
                              icon: Icon(
                                dangPhatAudio ? Icons.pause_circle_filled : Icons.play_circle_fill,
                                color: Colors.blueAccent,
                              ),
                              onPressed: () => phatHoacDungAudio(audioUrl),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    dangPhatAudio ? 'Đang phát audio nghe TOEIC...' : 'Đoạn băng nghe TOEIC (Audio)',
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.black87),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    dangPhatAudio ? 'Nhấn Pause để tạm dừng' : 'Nhấn nút Play để nghe giọng đọc chuẩn Mỹ / Anh',
                                    style: TextStyle(color: Colors.grey[700], fontSize: 12),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],

                    Card(
                      elevation: 1,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Only Reading passages are displayed during the test.
                            if (!isListening &&
                                cauHoi['context'] != null &&
                                cauHoi['context'].toString().isNotEmpty) ...[
                              Container(
                                padding: const EdgeInsets.all(16),
                                width: double.infinity,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.grey[300]!, width: 1.2),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        const Icon(Icons.article_outlined, size: 20, color: Colors.indigoAccent),
                                        const SizedBox(width: 8),
                                        const Text(
                                          'Đoạn văn đọc hiểu:',
                                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.indigoAccent),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 10),
                                    Divider(height: 1, color: Colors.grey[300]!),
                                    const SizedBox(height: 12),
                                    Text(
                                      cauHoi['context'],
                                      style: const TextStyle(
                                        fontSize: 16.0,
                                        height: 1.6,
                                        color: Colors.black87,
                                        fontWeight: FontWeight.normal,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 16),
                            ],
                            Text(
                              'Câu $cauTongSo: ${cauHoi['question_text'] ?? ''}',
                              style: const TextStyle(fontSize: 16.5, fontWeight: FontWeight.bold, height: 1.4),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 16),

                    ...List.generate((cauHoi['options'] as List).length, (index) {
                      final luaChon = cauHoi['options'][index];
                      final duocChon = dapAnChon == index;

                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: InkWell(
                          onTap: () => chonDapAn(index),
                          borderRadius: BorderRadius.circular(10),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                            decoration: BoxDecoration(
                              color: duocChon ? Colors.blue[50] : Colors.white,
                              borderRadius: BorderRadius.circular(10),
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

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: Colors.grey[200]!)),
              ),
              child: Row(
                children: [
                  if (cauHienTaiTrongChang > 0)
                    Expanded(
                      child: OutlinedButton(
                        onPressed: quayLaiCauTruoc,
                        child: const Text('Câu trước'),
                      ),
                    ),
                  if (cauHienTaiTrongChang > 0) const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: chuyenCauTiepTheo,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: changHienTai == 1 ? Colors.blueAccent : Colors.deepPurple,
                        foregroundColor: Colors.white,
                      ),
                      child: Text(
                        cauHienTaiTrongChang < danhSachCauHoiHienTai.length - 1
                            ? 'Câu tiếp theo'
                            : (changHienTai == 1 ? 'Chuyển sang Chặng 2' : 'Nộp bài thi'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    // ==================== GIAI DOAN 2: MAN HINH KET QUA TEST DAU VAO & XEP LOP ====================
    return Scaffold(
      appBar: AppBar(
        title: const Text('Hồ sơ Năng lực TOEIC (PCAT + NCD)'),
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Center(
              child: Icon(Icons.military_tech, size: 72, color: Colors.amber),
            ),
            const SizedBox(height: 12),
            const Text(
              'Kết quả bài làm PCAT',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Hồ sơ NCD chẩn đoán năng lực trên nội dung câu hỏi',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 20),

             // Raw evidence; a 20-item adaptive test is not an equated TOEIC score.
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
              ),
              child: Column(
                children: [
                  const Text('Số câu trả lời đúng', style: TextStyle(color: Colors.black54)),
                  const SizedBox(height: 6),
                  Text(
                    '$soCauDungTong / 20',
                    style: const TextStyle(fontSize: 38, fontWeight: FontWeight.bold, color: Colors.blueAccent),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Tỷ lệ đúng: ${(soCauDungTong / 20.0 * 100).toStringAsFixed(1)}%',
                    style: TextStyle(color: Colors.grey[700], fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                  const Divider(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          const Text('Listening', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text('Đúng $soCauDungNghe / 10 câu', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                        ],
                      ),
                      Column(
                        children: [
                          const Text('Reading', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text('Đúng $soCauDungDoc / 10 câu', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ================= BANG DANH GIA 7 PART TOEIC =================
            if (danhSachPartSummary.isNotEmpty) ...[
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.assessment, color: Colors.indigoAccent),
                          SizedBox(width: 8),
                          Text('Đánh giá chi tiết 7 Part TOEIC:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chỉ số NCD trên Part đã có câu hỏi; kèm số câu đúng để đối chiếu',
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                      const SizedBox(height: 12),
                      ...danhSachPartSummary.map((ps) {
                        final bool assessed = ps['is_assessed'] == true;
                        final int pNum = ps['part'] ?? 1;
                        final String pName = ps['part_name'] ?? 'Part $pNum';
                        final int qCnt = ps['question_count'] ?? 0;
                        final int cCnt = ps['correct_count'] ?? 0;
                        final num? scoreNum = ps['score_pct'];
                        final double score = scoreNum?.toDouble() ?? 0.0;

                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 6),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            decoration: BoxDecoration(
                              color: assessed ? (score >= 65 ? Colors.green[50] : Colors.blue[50]) : Colors.grey[50],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: assessed ? (score >= 65 ? Colors.green[200]! : Colors.blue[200]!) : Colors.grey[200]!,
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      pNum <= 4 ? Icons.headphones : Icons.menu_book,
                                      size: 18,
                                      color: assessed ? (pNum <= 4 ? Colors.indigo : Colors.orange[800]) : Colors.grey,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      pName,
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 13,
                                        color: assessed ? Colors.black87 : Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                                if (assessed)
                                  Row(
                                    children: [
                                      Text(
                                        'Đúng $cCnt/$qCnt câu',
                                        style: TextStyle(color: Colors.grey[700], fontSize: 12),
                                      ),
                                      const SizedBox(width: 10),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: score >= 65 ? Colors.green : (score >= 50 ? Colors.blueAccent : Colors.orange),
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        child: Text(
                                          '${score.toStringAsFixed(1)}%',
                                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                                        ),
                                      ),
                                    ],
                                  )
                                else
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: Colors.grey[300],
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: const Text(
                                      'Chưa đánh giá (N/A)',
                                      style: TextStyle(color: Colors.black54, fontSize: 11, fontStyle: FontStyle.italic),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            if (diemManh.isNotEmpty || diemYeu.isNotEmpty) ...[
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (diemManh.isNotEmpty) ...[
                        const Row(
                          children: [
                            Icon(Icons.star, color: Colors.amber, size: 20),
                            SizedBox(width: 8),
                            Text('Kỹ năng có chỉ số NCD cao (từ 3 câu):', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          children: diemManh.map((s) => Chip(
                            label: Text('${s['concept_name']}: ${s['score_pct']}%'),
                            backgroundColor: Colors.green[50],
                          )).toList(),
                        ),
                        if (diemYeu.isNotEmpty) const Divider(height: 20),
                      ],
                      if (diemYeu.isNotEmpty) ...[
                        const Row(
                          children: [
                            Icon(Icons.warning_amber_rounded, color: Colors.redAccent, size: 20),
                            SizedBox(width: 8),
                            Text('Kỹ năng có chỉ số NCD thấp (từ 3 câu):', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          children: diemYeu.map((s) => Chip(
                            label: Text('${s['concept_name']}: ${s['score_pct']}%'),
                            backgroundColor: Colors.red[50],
                          )).toList(),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            if (danhSachKyNangRadar.isNotEmpty) ...[
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.radar, color: Colors.blueAccent),
                          SizedBox(width: 8),
                          Text('Chỉ số NCD theo Part và nhãn EdNet:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chỉ hiển thị các kỹ năng đã được khảo sát câu hỏi trong đề thi',
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                      const SizedBox(height: 12),
                      ...danhSachKyNangRadar.where((s) => s['is_assessed'] == true).map((skill) {
                        final num? rawScore = skill['score_pct'];
                        final double score = rawScore?.toDouble() ?? 0.0;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(skill['concept_name'], style: const TextStyle(fontSize: 13)),
                                  Text('${score.toStringAsFixed(1)}% (${skill['correct_count']}/${skill['question_count']})', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                                ],
                              ),
                              const SizedBox(height: 4),
                              LinearProgressIndicator(
                                value: (score / 100.0).clamp(0.0, 1.0),
                                backgroundColor: Colors.grey[200],
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  score >= 70 ? Colors.green : (score >= 50 ? Colors.blue : Colors.orange),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],

            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.lightbulb_outline, color: Colors.amber),
                        SizedBox(width: 8),
                        Text('Ghi chú đánh giá:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Hồ sơ chẩn đoán nhận thức NCD được ước lượng từ mô hình thích ứng PCAT dựa trên dữ liệu chuẩn EdNet.',
                      style: const TextStyle(fontSize: 14, height: 1.5),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 28),

            ElevatedButton(
              onPressed: batDauLoTrinhDeXuat,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: const Text('BẮT ĐẦU HỌC THEO LỘ TRÌNH NÀY', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            ),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: lamLaiTest,
              child: const Text('Làm lại bài kiểm tra đầu vào'),
            ),
          ],
        ),
      ),
    );
  }
}
