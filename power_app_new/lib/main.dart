import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:fl_chart/fl_chart.dart';

void main() {
  runApp(const PowerApp());
}

class PowerApp extends StatelessWidget {
  const PowerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
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
  List<int> numbers = [];
  int second = 0;
  List stats = [];
  bool loading = false;

  final baseUrl = "https://power-lottery-ai.onrender.com";

  Future<void> fetchPredict() async {
    setState(() => loading = true);

    final res = await http.get(
      Uri.parse("$baseUrl/predict?strategy=$strategy"),
    );

    final data = jsonDecode(res.body);

    setState(() {
      numbers = List<int>.from(data["first_zone"]);
      second = data["second_zone"];
      loading = false;
    });
  }

  Future<void> fetchStats() async {
    final res = await http.get(Uri.parse("$baseUrl/stats"));
    stats = jsonDecode(res.body);
    setState(() {});
  }

  Widget ball(int n, Color c) => Container(
        margin: const EdgeInsets.all(6),
        width: 55,
        height: 55,
        decoration: BoxDecoration(
          color: c,
          shape: BoxShape.circle,
        ),
        child: Center(
            child: Text("$n",
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold))),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🎯 威力彩 AI 分析系統")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButton(
              value: strategy,
              items: const [
                DropdownMenuItem(value: "ai", child: Text("🧠 AI權重")),
                DropdownMenuItem(value: "hot", child: Text("🔥 熱號")),
                DropdownMenuItem(value: "cold", child: Text("❄ 冷號")),
                DropdownMenuItem(value: "random", child: Text("🎲 隨機")),
              ],
              onChanged: (v) => setState(() => strategy = v!),
            ),

            const SizedBox(height: 10),

            ElevatedButton(
              onPressed: loading ? null : fetchPredict,
              child: const Text("開始計算"),
            ),

            const SizedBox(height: 20),

            Wrap(
              alignment: WrapAlignment.center,
              children:
                  numbers.map((n) => ball(n, Colors.red)).toList(),
            ),

            if (second != 0) ball(second, Colors.blue),

            const SizedBox(height: 30),

            ElevatedButton(
              onPressed: fetchStats,
              child: const Text("📊 查看統計分析"),
            ),

            const SizedBox(height: 20),

            if (stats.isNotEmpty)
              SizedBox(
                height: 300,
                child: BarChart(
                  BarChartData(
                    barGroups: stats.map<BarChartGroupData>((e) {
                      return BarChartGroupData(
                        x: e["num"],
                        barRods: [
                          BarChartRodData(
                            toY: e["count"].toDouble(),
                            width: 5,
                            color: Colors.deepPurple,
                          )
                        ],
                      );
                    }).toList(),
                    titlesData: FlTitlesData(
                      leftTitles: const AxisTitles(
                          sideTitles: SideTitles(showTitles: true)),
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          interval: 5,
                          getTitlesWidget: (v, _) =>
                              Text(v.toInt().toString(),
                                  style: const TextStyle(fontSize: 10)),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
