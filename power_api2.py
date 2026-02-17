from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import random

app = Flask(__name__)

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"

# ---------- Load Data ----------

def load_df():
    return pd.read_csv(CSV_PATH).dropna()

def load_nums():
    df = load_df()
    return df[[f"獎號{i}" for i in range(1, 7)]]

# ---------- Advanced AI Model ----------

def ai_advanced():
    df = load_df()

    # 近期資料加權（最近越高）
    df = df.tail(50)  # 只看最近50期
    weights = list(range(1, len(df) + 1))  # 越新越重

    counter = Counter()

    for idx, row in df.iterrows():
        weight = weights[idx - df.index[0]]
        for i in range(1, 7):
            counter[int(row[f"獎號{i}"])] += weight

    pool = list(range(1, 39))
    weight_list = [counter.get(n, 1) for n in pool]

    result = []
    while len(result) < 6:
        pick = random.choices(pool, weights=weight_list, k=1)[0]
        if pick not in result:
            result.append(pick)

    return sorted(result)

# ---------- Hot / Cold Improved ----------

def hot():
    nums = load_nums().values.flatten()
    counter = Counter(nums)
    hot_nums = [n for n, _ in counter.most_common(6)]
    return sorted(hot_nums)

def cold():
    nums = load_nums().values.flatten()
    counter = Counter(nums)
    base = list(range(1, 39))
    cold_nums = sorted(base, key=lambda x: counter.get(x, 0))[:6]

    # 加入反彈概率
    if random.random() < 0.3:
        cold_nums[random.randint(0,5)] = random.choice(base)

    return sorted(set(cold_nums))[:6]

def random_pick():
    return sorted(random.sample(range(1, 39), 6))

def second_zone():
    df = load_df()
    return int(random.choice(df["第二區"].tolist()))

# ---------- Routes ----------

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
        z1 = ai_advanced()

    return jsonify({
        "first_zone": z1,
        "second_zone": second_zone(),
        "strategy": strategy
    })

@app.route("/stats")
def stats():
    nums = load_nums().values.flatten()
    counter = Counter(nums)

    result = []
    for i in range(1, 39):
        result.append({
            "num": i,
            "count": counter.get(i, 0)
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
