import 'package:flutter/material.dart';
import 'man_hinh/dang_nhap.dart';

/// Ham main() la diem khoi dau cua toan bo ung dung Flutter.
/// Su dung ham runApp() de dua widget goc (root widget) vao cay Widget Tree va render len man hinh.
void main() {
  runApp(const UngDungGetGoals());
}

/// Lop ung dung chinh: UngDungGetGoals
/// Ke thua StatelessWidget vi cau hinh tong the cua ung dung (theme, routing) la co dinh, khong thay doi trang thai noi tai.
class UngDungGetGoals extends StatelessWidget {
  const UngDungGetGoals({super.key});

  @override
  Widget build(BuildContext context) {
    // WIDGET: MaterialApp
    // Vai tro: Cung cap bo khung thiet ke chuan Material Design cua Google cho toan bo app.
    // Cach hoat dong: Quan ly cac he thong toan cuc nhu Navigator (dieu huong trang), Theme (mau sac, phong chu),
    // va cac thiet lap da ngon ngu, debug banner.
    return MaterialApp(
      title: 'GetGoals - Luyen Thi TOEIC',
      debugShowCheckedModeBanner: false, // Tat dai banner chu "DEBUG" o goc phai man hinh cho giao dien dep mat

      // WIDGET/OBJECT: ThemeData
      // Vai tro: Thiet lap he mau va phong cach giao dien dong nhat xuyen suot tat ca cac man hinh.
      theme: ThemeData(
        useMaterial3: true, // Kich hoat phien ban Material Design 3 moi nhat cua Google

        // ColorScheme.fromSeed: Tu dong tao ra mot bang mau hai hoa dua tren 1 mau chu dao (seedColor: blueAccent)
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blueAccent,
          primary: Colors.blueAccent,
        ),

        // Mau nen toan cuc cua Scaffold: Mau trang xam nhe (0xFFF8FAFC) giup mat de chiu khi doc de thi lau
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        cardColor: Colors.white,

        // AppBarTheme: Dinh nghia phong cach mac dinh cho tat ca thanh tieu de (AppBar) tren toan ung dung
        appBarTheme: const AppBarTheme(
          centerTitle: false, // Tieu de can trai kieu hien dai
          elevation: 0,       // Khong do bong dam de giu phong cach phang (Flat UI)
          backgroundColor: Colors.white,
          foregroundColor: Colors.black87,
        ),
      ),

      // Thuoc tinh home: Man hinh dau tien duoc hien thi khi nguoi dung khoi dong ung dung.
      // O day mac dinh dan vao man hinh DangNhapManHinh.
      home: const DangNhapManHinh(),
    );
  }
}
