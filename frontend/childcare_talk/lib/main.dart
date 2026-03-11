import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'screens/login_screen.dart';
import 'screens/conversation_list_screen.dart';

void main() {
  runApp(const ChildcareTalkApp());
}

class ChildcareTalkApp extends StatelessWidget {
  const ChildcareTalkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '육아톡',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFFF8F00),
        ),
        useMaterial3: true,
      ),
      home: const SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final api = ApiService();
    final loggedIn = await api.isLoggedIn();

    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) =>
              loggedIn ? const ConversationListScreen() : const LoginScreen(),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFFFFF8E1),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('🍼', style: TextStyle(fontSize: 64)),
            SizedBox(height: 16),
            Text(
              '육아톡',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Color(0xFFFF8F00),
              ),
            ),
            SizedBox(height: 24),
            CircularProgressIndicator(color: Color(0xFFFF8F00)),
          ],
        ),
      ),
    );
  }
}
