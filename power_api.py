from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import math
import os
import requests
from io import StringIO

app = Flask(__name__)

HISTORY_FILE = "weli_history.csv"
LATEST_FILE = "weli_latest.csv"

DATA_URL = "https://raw.githubusercontent.com/Jeffrey1616/taiwan-lottery-data/master/powerlotto.csv"


# =========================
# 下載並同步完整資料庫
# =========================

def sync_latest():
    print("📡 同步完整歷史資料庫...")

    r = requests.get(DATA_URL, timeout=20)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text))

    df.columns = [
        "開獎日期","獎號1","獎號2","獎號3",
        "獎號4","獎號5","獎號6","第二區"
    ]

    # 存完整歷史
    df.to_csv(HISTORY_FILE, index=False, encoding="utf-8-sig")

    # 存最近 100 期給快速分析
    df.tail(100).to_csv(LATEST_FILE, index=False, encoding="utf-8-sig")

    print(f"✅ 歷史期數：{len(df)}")
    print("🔥 最近 100 期同步完成")


# =========================
# 載入資料
# =========================

def load_numbers(use_latest=True):
    file = LATEST_FILE if use_latest else HISTORY_FILE
    df = pd.read_csv(file)

    nums = []
    specials = []

    for _, row in df.iterrows():
        nums.extend([
            int(row["獎號1"]), int(row["獎號2"]), int(row["獎號3"]),
            int(row["獎號4"]), int(row["獎號5"]), int(row["獎號6"])
        ])
        specials.append(int(row["第二區"]))

    return nums, specials


# =========================
# 機率模型（非亂數）
# =========================

def softmax(scores):
    m = max(scores.values())
    exps = {k: math.exp(v - m) for k, v in scores.items()}
    s = sum(exps.values())
    return {k: exps[k] / s for k in exps}


def weighted_pick(prob_map, k):
    return random.choices(
        list(prob_map.keys()),
        list(prob_map.values()),
        k=k
    )


# =========================
# 統計 API（近期）
# =========================

@app.route("/stats")
def stats():
    nums, _ = load_numbers(True)
    c = Counter(nums)

    return jsonify([
        {"num": i, "count": c.get(i, 0)}
        for i in range(1, 39)
    ])


# =========================
# AI 預測（長短期混合）
# =========================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    recent_nums, specials = load_numbers(True)
    all_nums, _ = load_numbers(False)

    recent_c = Counter(recent_nums)
    long_c = Counter(all_nums)

    scores = {}

    for i in range(1, 39):
        scores[i] = recent_c.get(i, 0) * 1.5 + long_c.get(i, 0) * 0.5

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
    sync_latest()
    app.run(host="0.0.0.0", port=10000)
