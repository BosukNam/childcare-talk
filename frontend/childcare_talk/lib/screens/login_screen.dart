import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'conversation_list_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _nicknameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _api = ApiService();
  bool _isLoading = false;
  bool _isRegisterMode = false;
  String? _error;

  Future<void> _submit() async {
    final nickname = _nicknameController.text.trim();
    final password = _passwordController.text.trim();
    if (nickname.isEmpty || password.isEmpty) {
      setState(() => _error = '닉네임과 비밀번호를 입력해주세요');
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    bool success;
    if (_isRegisterMode) {
      success = await _api.register(nickname, password);
      if (!success) _error = '이미 사용 중인 닉네임이에요';
    } else {
      success = await _api.login(nickname, password);
      if (!success) _error = '닉네임 또는 비밀번호가 틀렸어요';
    }

    setState(() => _isLoading = false);

    if (success && mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => const ConversationListScreen(),
        ),
      );
    }
  }

  @override
  void dispose() {
    _nicknameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF8E1),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                '🍼',
                style: TextStyle(fontSize: 64),
              ),
              const SizedBox(height: 16),
              const Text(
                '육아톡',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFFF8F00),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '친구같은 육아 상담사',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 48),
              TextField(
                controller: _nicknameController,
                decoration: InputDecoration(
                  labelText: '닉네임',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: const Icon(Icons.person_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: '비밀번호',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: const Icon(Icons.lock_outline),
                ),
                onSubmitted: (_) => _submit(),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF8F00),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : Text(_isRegisterMode ? '회원가입' : '로그인'),
                ),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  setState(() {
                    _isRegisterMode = !_isRegisterMode;
                    _error = null;
                  });
                },
                child: Text(
                  _isRegisterMode
                      ? '이미 계정이 있어요? 로그인'
                      : '처음이에요? 회원가입',
                  style: const TextStyle(color: Color(0xFFFF8F00)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
