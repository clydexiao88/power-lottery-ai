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

  List<int> firstZone = [];
  int? secondZone;
  bool loading = false;

  List<Map<String, dynamic>> stats = [];

  Future<void> fetchPrediction() async {
    try {
      setState(() => loading = true);

      final url =
          Uri.parse("http://192.168.1.107:5000/predict?strategy=$strategy");
      final res = await http.get(url);
      final data = jsonDecode(res.body);

      setState(() {
        firstZone = List<int>.from(data["first_zone"]);
        secondZone = data["second_zone"];
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("連線錯誤：$e")));
    }
  }

  Future<void> fetchStats() async {
    try {
      final url = Uri.parse("http://192.168.1.107:5000/stats");
      final res = await http.get(url);
      final data = jsonDecode(res.body);

      setState(() {
        stats = List<Map<String, dynamic>>.from(data);
      });
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("統計讀取失敗：$e")));
    }
  }

  Widget ball(int num, {Color color = Colors.red}) {
    return Container(
      margin: const EdgeInsets.all(6),
      width: 48,
      height: 48,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: const [
          BoxShadow(color: Colors.black26, blurRadius: 6),
        ],
      ),
      child: Text(
        num.toString(),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget statsChart(List<Map<String, dynamic>> data) {
    if (data.isEmpty) return const SizedBox();

    int maxCount =
        data.map((e) => e["count"] as int).reduce((a, b) => a > b ? a : b);

    return SizedBox(
      height: 320,
      child: BarChart(
        BarChartData(
          maxY: maxCount.toDouble() + 1,

          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 1,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: const TextStyle(fontSize: 10),
                  );
                },
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 3,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: const TextStyle(fontSize: 8),
                  );
                },
              ),
            ),
            rightTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),

          borderData: FlBorderData(show: false),

          barGroups: data.map((e) {
            int c = e["count"];

            Color color = c > maxCount * 0.7
                ? Colors.red
                : c < maxCount * 0.3
                    ? Colors.blue
                    : Colors.orange;

            return BarChartGroupData(
              x: e["num"],
              barRods: [
                BarChartRodData(
                  toY: c.toDouble(),
                  width: 6,
                  color: color,
                  borderRadius: BorderRadius.circular(4),
                )
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🎯 威力彩 AI 分析系統")),
      body: SingleChildScrollView(
        child: Center(
          child: Column(
            children: [
              const SizedBox(height: 20),

              DropdownButton<String>(
                value: strategy,
                items: const [
                  DropdownMenuItem(value: "ai", child: Text("🧠 AI權重")),
                  DropdownMenuItem(value: "hot", child: Text("🔥 熱號策略")),
                  DropdownMenuItem(value: "cold", child: Text("🧊 冷號策略")),
                  DropdownMenuItem(value: "random", child: Text("🎲 完全隨機")),
                ],
                onChanged: (v) => setState(() => strategy = v!),
              ),

              ElevatedButton(
                onPressed: loading ? null : fetchPrediction,
                child: const Text("開始計算"),
              ),

              ElevatedButton(
                onPressed: fetchStats,
                child: const Text("📊 查看統計分析"),
              ),

              const SizedBox(height: 20),

              if (loading) const CircularProgressIndicator(),

              if (firstZone.isNotEmpty) ...[
                Wrap(
                  alignment: WrapAlignment.center,
                  children: firstZone.map((n) => ball(n)).toList(),
                ),
                const SizedBox(height: 12),
                if (secondZone != null)
                  ball(secondZone!, color: Colors.blue),
              ],

              const SizedBox(height: 20),

              if (stats.isNotEmpty) statsChart(stats),

              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }
}
