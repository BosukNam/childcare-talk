import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/conversation.dart';
import '../models/message.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  String? _token;

  Future<String?> get token async {
    if (_token != null) return _token;
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    return _token;
  }

  Future<Map<String, String>> get _headers async {
    final t = await token;
    return {
      'Content-Type': 'application/json',
      if (t != null) 'Authorization': 'Bearer $t',
    };
  }

  Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  // Auth
  Future<bool> register(String nickname, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'nickname': nickname, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveToken(data['access_token']);
      return true;
    }
    return false;
  }

  Future<bool> login(String nickname, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'nickname': nickname, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveToken(data['access_token']);
      return true;
    }
    return false;
  }

  Future<bool> isLoggedIn() async {
    final t = await token;
    if (t == null) return false;
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: await _headers,
    );
    return response.statusCode == 200;
  }

  // Conversations
  Future<List<Conversation>> getConversations() async {
    final response = await http.get(
      Uri.parse('$baseUrl/conversations'),
      headers: await _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Conversation.fromJson(e)).toList();
    }
    return [];
  }

  Future<Conversation?> createConversation() async {
    final response = await http.post(
      Uri.parse('$baseUrl/conversations'),
      headers: await _headers,
    );
    if (response.statusCode == 200) {
      return Conversation.fromJson(jsonDecode(response.body));
    }
    return null;
  }

  Future<void> deleteConversation(String id) async {
    await http.delete(
      Uri.parse('$baseUrl/conversations/$id'),
      headers: await _headers,
    );
  }

  Future<List<Message>> getMessages(String conversationId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/conversations/$conversationId/messages'),
      headers: await _headers,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Message.fromJson(e)).toList();
    }
    return [];
  }

  // Chat (SSE streaming)
  Stream<String> sendMessage(String conversationId, String content) async* {
    final headers = await _headers;
    final request = http.Request(
      'POST',
      Uri.parse('$baseUrl/chat/$conversationId'),
    );
    request.headers.addAll(headers);
    request.body = jsonEncode({'content': content});

    final response = await http.Client().send(request);
    final stream = response.stream
        .transform(utf8.decoder)
        .transform(const LineSplitter());

    await for (final line in stream) {
      if (line.startsWith('data: ')) {
        final jsonStr = line.substring(6);
        try {
          final data = jsonDecode(jsonStr);
          if (data['type'] == 'chunk') {
            yield data['content'];
          } else if (data['type'] == 'done') {
            return;
          } else if (data['type'] == 'error') {
            throw Exception(data['content']);
          }
        } catch (_) {}
      }
    }
  }
}
