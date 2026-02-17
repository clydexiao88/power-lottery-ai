from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import random

app = Flask(__name__)

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"

# ---------- Data Loading ----------

def load_nums():
    df = pd.read_csv(CSV_PATH).dropna()
    nums = df[[f"獎號{i}" for i in range(1, 7)]].values.flatten()
    return [int(n) for n in nums]

def load_second():
    df = pd.read_csv(CSV_PATH).dropna()
    return [int(n) for n in df["第二區"].tolist()]

# ---------- Strategy Engines ----------

def ai_weight():
    nums = load_nums()
    counter = Counter(nums)

    pool = list(range(1, 39))
    weights = [counter.get(n, 0) + 1 for n in pool]

    result = []
    while len(result) < 6:
        pick = random.choices(pool, weights=weights, k=1)[0]
        if pick not in result:
            result.append(pick)

    return sorted(result)

def hot():
    nums = load_nums()
    counter = Counter(nums)
    hot_nums = [n for n, _ in counter.most_common(6)]

    if len(hot_nums) < 6:
        hot_nums += random.sample(
            [n for n in range(1, 39) if n not in hot_nums],
            6 - len(hot_nums)
        )

    return sorted(hot_nums)

def cold():
    nums = load_nums()
    counter = Counter(nums)
    base = list(range(1, 39))

    cold_nums = sorted(base, key=lambda x: counter.get(x, 0))[:6]

    if len(cold_nums) < 6:
        cold_nums += random.sample(
            [n for n in base if n not in cold_nums],
            6 - len(cold_nums)
        )

    return sorted(cold_nums)

def random_pick():
    return sorted(random.sample(range(1, 39), 6))

def second_zone():
    return random.choice(load_second())

# ---------- API Routes ----------

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    if strategy == "hot":
        z1 = hot()
    elif strategy == "cold":
        z1 = cold()
    elif strategy == "random":
        z1 = random_pick()
    else:
        z1 = ai_weight()

    return jsonify({
        "first_zone": z1,
        "second_zone": second_zone(),
        "strategy": strategy
    })

@app.route("/stats")
def stats():
    nums = load_nums()
    counter = Counter(nums)

    result = []
    for i in range(1, 39):
        result.append({
            "num": i,
            "count": counter.get(i, 0)
        })

    return jsonify(result)

# ---------- Server ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
