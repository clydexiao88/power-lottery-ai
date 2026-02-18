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
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(),
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
  bool loading = false;

  List<int> firstZone = [];
  int secondZone = 0;

  List stats = [];

  final String baseUrl = "https://power-lottery-ai.onrender.com";

  @override
  void initState() {
    super.initState();
    fetchStats(); // ⭐ 一進畫面就自動載入統計圖表
  }

  Future<void> fetchPrediction() async {
    setState(() => loading = true);

    final res = await http.get(
      Uri.parse("$baseUrl/predict?strategy=$strategy"),
    );

    final data = jsonDecode(res.body);

    setState(() {
      firstZone = List<int>.from(data["first_zone"]);
      secondZone = data["second_zone"];
      loading = false;
    });
  }

  Future<void> fetchStats() async {
    final res = await http.get(
      Uri.parse("$baseUrl/stats"),
    );

    setState(() {
      stats = jsonDecode(res.body);
    });
  }

  Widget ball(int n, Color c) => Container(
        width: 48,
        height: 48,
        margin: const EdgeInsets.all(5),
        decoration: BoxDecoration(
          color: c,
          shape: BoxShape.circle,
        ),
        alignment: Alignment.center,
        child: Text(
          "$n",
          style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold),
        ),
      );

  List<BarChartGroupData> buildBars() {
    return stats.map<BarChartGroupData>((e) {
      return BarChartGroupData(
        x: e["num"],
        barRods: [
          BarChartRodData(
            toY: (e["count"] as num).toDouble(),
            width: 6,
            color: Colors.deepPurple,
          )
        ],
      );
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🎯 威力彩 AI 分析系統")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            DropdownButton(
              value: strategy,
              items: const [
                DropdownMenuItem(value: "ai", child: Text("🧠 AI")),
                DropdownMenuItem(value: "hot", child: Text("🔥 熱號")),
                DropdownMenuItem(value: "cold", child: Text("❄ 冷號")),
                DropdownMenuItem(value: "random", child: Text("🎲 隨機")),
              ],
              onChanged: (v) => setState(() => strategy = v!),
            ),

            const SizedBox(height: 12),

            ElevatedButton(
              onPressed: loading ? null : fetchPrediction,
              child: loading
                  ? const CircularProgressIndicator()
                  : const Text("開始計算"),
            ),

            const SizedBox(height: 18),

            Wrap(
              alignment: WrapAlignment.center,
              children:
                  firstZone.map((n) => ball(n, Colors.red)).toList(),
            ),

            if (secondZone != 0)
              ball(secondZone, Colors.blue),

            const SizedBox(height: 30),

            const Text("📊 歷史數據統計圖",
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.bold)),

            const SizedBox(height: 12),

            if (stats.isNotEmpty)
              SizedBox(
                height: 280,
                child: BarChart(
                  BarChartData(
                    barGroups: buildBars(),
                    gridData: FlGridData(show: true),
                    borderData: FlBorderData(show: true),
                    titlesData: FlTitlesData(
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          interval: 5,
                          getTitlesWidget: (v, _) =>
                              Text(v.toInt().toString(),
                                  style: const TextStyle(fontSize: 10)),
                        ),
                      ),
                      leftTitles: AxisTitles(
                        sideTitles:
                            SideTitles(showTitles: true),
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
