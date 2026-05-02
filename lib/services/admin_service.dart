import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/admin_dashboard.dart';
import '../config.dart';

class AdminService {
  static const String apiBase = apiBaseUrl;

  static Future<AdminDashboard?> fetchDashboard() async {
    // Use new API location if routed via base: admin_dashboard.php
    final url = Uri.parse('${apiBase}admin_dashboard.php');
    try {
      final resp = await http.get(url).timeout(const Duration(seconds: 10));
      final body = resp.body.trim();
      if (resp.statusCode == 200) {
        if (body.isEmpty || !(body.startsWith('{') || body.startsWith('['))) {
          throw Exception(
              'Non-JSON response from API: ${body.substring(0, body.length.clamp(0, 200))}');
        }
        final Map<String, dynamic> decoded = jsonDecode(body);
        if (decoded['success'] == true) {
          final payload = decoded['data'] ?? <String, dynamic>{};
          return AdminDashboard.fromJson(payload);
        } else {
          throw Exception(
              'API returned error: ${decoded['error']?.toString() ?? body}');
        }
      } else {
        throw Exception(
            'HTTP ${resp.statusCode}: ${body.substring(0, body.length.clamp(0, 200))}');
      }
    } catch (e) {
      rethrow;
    }
  }

  static Future<List<Map<String, dynamic>>> fetchUsers(
      {String status = 'all'}) async {
    final url = Uri.parse('${apiBase}get_users.php').replace(queryParameters: {
      'status': status,
    });
    try {
      final resp = await http.get(url).timeout(const Duration(seconds: 10));
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body);
        if (body['success'] == true) {
          return List<Map<String, dynamic>>.from(body['users']);
        }
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  static Future<bool> updateUserStatus(String userId, String action) async {
    final url = Uri.parse('${apiBase}update_user_status.php');
    try {
      final resp = await http.post(
        url,
        body: jsonEncode({'user_id': userId, 'action': action}),
        headers: {'Content-Type': 'application/json'},
      );
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body);
        return body['success'] == true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
