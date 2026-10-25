import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:getgoals_frontend/man_hinh/kiem_tra_dau_vao.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  testWidgets('Incomplete optimized paper is shown as unavailable', (tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());

    final client = MockClient((request) async {
      expect(request.url.path, '/api/pcat/stage1');
      return http.Response(
        jsonEncode({'detail': 'Bộ đề PCAT tối ưu chưa đủ nội dung, ảnh hoặc audio để mở bài thi.'}),
        503,
        headers: {'content-type': 'application/json; charset=utf-8'},
      );
    });
    addTearDown(client.close);

    await tester.pumpWidget(MaterialApp(home: KiemTraDauVaoManHinh(client: client)));
    expect(find.text('Đề thi test trình độ'), findsWidgets);
    await tester.tap(find.text('BẮT ĐẦU LÀM BÀI TEST THÍCH ỨNG NGAY'));
    await tester.pumpAndSettle();

    expect(find.text('Bộ đề PCAT tối ưu chưa đủ nội dung, ảnh hoặc audio để mở bài thi.'), findsOneWidget);
    expect(find.text('Chuyển sang Chặng 2'), findsNothing);
  });
}
