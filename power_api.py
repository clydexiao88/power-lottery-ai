from flask import Flask, jsonify, request
import csv
import random
from collections import Counter
import math
import os

app = Flask(__name__)

CSV_FILE = "weli_20260.csv"

# ---------- Load CSV ----------

def load_numbers():
    nums = []
    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for i in range(1, 7):
                nums.append(int(row[f"獎號{i}"]))
    return nums


# ---------- Softmax with safety ----------

def softmax(scores):
    if not scores:
        return {}

    max_score = max(scores.values())
    exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
    total = sum(exp_scores.values())

    if total == 0:
        return {}

    return {k: v / total for k, v in exp_scores.items()}


# ---------- Weighted pick ----------

def weighted_sample(prob_map, k):
    if not prob_map:
        return random.sample(range(1, 39), k)

    nums = list(prob_map.keys())
    weights = list(prob_map.values())

    chosen = set()
    while len(chosen) < k:
        chosen.add(random.choices(nums, weights=weights)[0])

    return sorted(chosen)


# ---------- Prediction logic ----------

def model_predict(strategy):
    history = load_numbers()
    counter = Counter(history)

    if strategy == "random":
        first_zone = sorted(random.sample(range(1, 39), 6))

    elif strategy == "hot":
        ranked = counter.most_common(20)
        pool = [n for n, _ in ranked]
        first_zone = sorted(random.sample(pool, 6))

    elif strategy == "cold":
        cold = sorted(counter.items(), key=lambda x: x[1])[:20]
        pool = [n for n, _ in cold]
        first_zone = sorted(random.sample(pool, 6))

    else:  # AI 機率模型（穩定版）
        weights = []
        nums = list(range(1, 39))

        for n in nums:
            weights.append(counter.get(n, 0) + 1)  # +1 防止歸零

        first_zone = sorted(random.choices(nums, weights=weights, k=6))
        first_zone = list(set(first_zone))

        while len(first_zone) < 6:
            first_zone.append(random.choice(nums))

        first_zone = sorted(first_zone)

    second_zone = random.randint(1, 8)

    return first_zone, second_zone

# ---------- API ----------

@app.route("/")
def home():
    return "Power Lottery AI API running with real CSV data"


@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    first, second = model_predict(strategy)

    return jsonify({
        "first_zone": first,
        "second_zone": second
    })


@app.route("/stats")
def stats():
    nums = load_numbers()
    counter = Counter(nums)

    return jsonify([
        {"num": i, "count": counter.get(i, 0)}
        for i in range(1, 39)
    ])


# ---------- Run ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
