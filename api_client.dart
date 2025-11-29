import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  final String baseUrl;

  ApiClient({this.baseUrl = 'http://localhost:8000'});

  Future<Map<String, dynamic>> getBalance(String network, String wallet) async {
    final response = await http.get(Uri.parse('$baseUrl/balance/$network/$wallet'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load balance');
    }
  }

  Future<Map<String, dynamic>> sendSol(String network, String wallet, String recipient, double amount) async {
    final response = await http.post(
      Uri.parse('$baseUrl/send_sol'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'network': network,
        'wallet': wallet,
        'recipient': recipient,
        'amount': amount,
      }),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to send SOL: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> sendTpc(String network, String wallet, String recipient, double amount) async {
    final response = await http.post(
      Uri.parse('$baseUrl/send_tpc'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'network': network,
        'wallet': wallet,
        'recipient': recipient,
        'amount': amount,
      }),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to send TPC: ${response.body}');
    }
  }

  Future<List<String>> getWallets() async {
    final response = await http.get(Uri.parse('$baseUrl/wallets'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return List<String>.from(data['wallets']);
    } else {
      throw Exception('Failed to load wallets');
    }
  }

  Future<List<String>> getNetworks() async {
    final response = await http.get(Uri.parse('$baseUrl/networks'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return List<String>.from(data['networks']);
    } else {
      throw Exception('Failed to load networks');
    }
  }
}

// Example usage in Flutter:
/*
void main() async {
  final api = ApiClient();

  // Get balance
  try {
    final balance = await api.getBalance('Devnet', 'Test Wallet');
    print('SOL: ${balance['sol_balance']}, TPC: ${balance['tpc_balance']}');
  } catch (e) {
    print(e);
  }

  // Send SOL
  try {
    final result = await api.sendSol('Devnet', 'Test Wallet', 'recipient_address', 0.1);
    print('Transaction sent: ${result['signature']}');
  } catch (e) {
    print(e);
  }

  // Similarly for sendTpc
}
*/</content>
<parameter name="filePath">/home/belikan/Topocoin/api_client.dart