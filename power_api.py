from flask import Flask, jsonify, request
import csv
import random
import math
from collections import defaultdict

app = Flask(__name__)

CSV_FILE = "weli_20260.csv"


def load_data():
    draws = []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                nums = list(map(int, row[:6]))
                draws.append(nums)
            except:
                continue
    return draws


# 📈 時間衰減 + 頻率加權
def calculate_scores(draws):
    scores = defaultdict(float)
    total_draws = len(draws)

    for idx, draw in enumerate(draws):
        # 越近期權重越高
        time_weight = (idx + 1) / total_draws
        for n in draw:
            scores[n] += 1.0 * time_weight

    return scores


# 🧠 Softmax 機率分布
def softmax(scores):
    max_score = max(scores.values())
    exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
    total = sum(exp_scores.values())
    probs = {k: v / total for k, v in exp_scores.items()}
    return probs


# 🎯 機率抽樣（不重複）
def weighted_sample(probs, k=6):
    selected = []
    pool = probs.copy()

    for _ in range(k):
        r = random.random()
        cumulative = 0
        for n, p in pool.items():
            cumulative += p
            if r <= cumulative:
                selected.append(n)
                pool.pop(n)
                # 重新正規化
                total = sum(pool.values())
                pool = {k: v / total for k, v in pool.items()}
                break
    return sorted(selected)


@app.route("/")
def home():
    return "Power Lottery AI API running with REAL probability model"


@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    draws = load_data()

    if strategy == "random":
        first_zone = random.sample(range(1, 39), 6)

    else:
        scores = calculate_scores(draws)

        if strategy == "hot":
            sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            first_zone = sorted([n for n, _ in sorted_nums[:6]])

        elif strategy == "cold":
            sorted_nums = sorted(scores.items(), key=lambda x: x[1])
            first_zone = sorted([n for n, _ in sorted_nums[:6]])

        else:  # 🧠 AI 模型
            probs = softmax(scores)
            first_zone = weighted_sample(probs)

    second_zone = random.randint(1, 8)

    return jsonify({
        "first_zone": first_zone,
        "second_zone": second_zone
    })


@app.route("/stats")
def stats():
    draws = load_data()
    counter = defaultdict(int)

    for draw in draws:
        for n in draw:
            counter[n] += 1

    result = []
    for i in range(1, 39):
        result.append({
            "num": i,
            "count": counter[i]
        })

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
