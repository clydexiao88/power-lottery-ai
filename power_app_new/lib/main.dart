import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const PowerApp());
}

class PowerApp extends StatelessWidget {
  const PowerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Power Lottery AI',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.red,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String strategy = "ai";

  List<int> firstZone = [];
  int secondZone = 0;

  bool loading = false;

  Future<void> fetchPrediction() async {
    setState(() => loading = true);

    final url = Uri.parse(
      "https://power-lottery-ai.onrender.com/predict?strategy=$strategy",
    );

    try {
      final res = await http.get(url);

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);

        setState(() {
          firstZone = List<int>.from(data["first_zone"]);
          secondZone = data["second_zone"];
        });
      }
    } catch (e) {
      debugPrint("連線錯誤: $e");
    }

    setState(() => loading = false);
  }

  Widget ball(int num, Color color) {
    return Container(
      width: 55,
      height: 55,
      margin: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 6,
            offset: Offset(2, 3),
          )
        ],
      ),
      alignment: Alignment.center,
      child: Text(
        "$num",
        style: const TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xfff6eef4),
      appBar: AppBar(
        title: const Text("🎯 威力彩 AI 分析系統"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          children: [
            DropdownButton<String>(
              value: strategy,
              items: const [
                DropdownMenuItem(value: "ai", child: Text("🧠 AI 權重")),
                DropdownMenuItem(value: "hot", child: Text("🔥 熱號策略")),
                DropdownMenuItem(value: "cold", child: Text("❄ 冷號策略")),
                DropdownMenuItem(value: "random", child: Text("🎲 完全隨機")),
              ],
              onChanged: (v) => setState(() => strategy = v!),
            ),
            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: loading ? null : fetchPrediction,
              style: ElevatedButton.styleFrom(
                padding:
                    const EdgeInsets.symmetric(horizontal: 40, vertical: 14),
              ),
              child: loading
                  ? const CircularProgressIndicator()
                  : const Text("開始計算"),
            ),

            const SizedBox(height: 30),

            Wrap(
              alignment: WrapAlignment.center,
              children:
                  firstZone.map((n) => ball(n, Colors.red)).toList(),
            ),

            if (secondZone != 0)
              Padding(
                padding: const EdgeInsets.only(top: 18),
                child: ball(secondZone, Colors.blue),
              ),
          ],
        ),
      ),
    );
  }
}
