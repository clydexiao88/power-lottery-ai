from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import math
import os

app = Flask(__name__)

DATA_FILE = "weli_latest.csv"   # 你的主資料庫


# =========================
# 載入資料
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("找不到 weli_latest.csv，請確認資料存在")

    df = pd.read_csv(DATA_FILE)

    nums = []
    specials = []

    for _, r in df.iterrows():
        nums += [
            int(r["獎號1"]), int(r["獎號2"]), int(r["獎號3"]),
            int(r["獎號4"]), int(r["獎號5"]), int(r["獎號6"])
        ]
        specials.append(int(r["第二區"]))

    return nums, specials


# =========================
# 機率工具
# =========================

def softmax(scores):
    m = max(scores.values())
    exps = {k: math.exp(v - m) for k, v in scores.items()}
    s = sum(exps.values())
    return {k: exps[k] / s for k in exps}


def weighted_pick(p, k):
    return random.choices(list(p.keys()), list(p.values()), k=k)


# =========================
# 統計 API
# =========================

@app.route("/stats")
def stats():
    nums, _ = load_data()
    c = Counter(nums)

    return jsonify([
        {"num": i, "count": c.get(i, 0)}
        for i in range(1, 39)
    ])


# =========================
# 預測 API（真機率）
# =========================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    nums, specials = load_data()
    counter = Counter(nums)

    scores = {i: counter.get(i, 0) for i in range(1, 39)}
    probs = softmax(scores)

    if strategy == "hot":
        picks = sorted(scores, key=scores.get, reverse=True)[:6]

    elif strategy == "cold":
        picks = sorted(scores, key=scores.get)[:6]

    else:
        picks = set(weighted_pick(probs, 6))
        while len(picks) < 6:
            picks.add(weighted_pick(probs, 1)[0])
        picks = sorted(picks)

    second = Counter(specials).most_common(1)[0][0]

    return jsonify({
        "first_zone": picks,
        "second_zone": second
    })


# =========================
# 啟動
# =========================

if __name__ == "__main__":
    print("✅ 使用本地歷史資料庫運算中")
    app.run(host="0.0.0.0", port=10000)
