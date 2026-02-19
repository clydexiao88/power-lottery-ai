from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import math

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/ycshih/taiwan-lottery-datasets/main/powerlotto.csv"
LOCAL_FILE = "weli_latest.csv"


# =========================
# 自動同步真實歷史資料
# =========================

def sync_latest():
    print("📡 同步歷史資料庫...")
    df = pd.read_csv(DATA_URL)

    df = df.rename(columns={
        "date": "開獎日期",
        "n1": "獎號1",
        "n2": "獎號2",
        "n3": "獎號3",
        "n4": "獎號4",
        "n5": "獎號5",
        "n6": "獎號6",
        "special": "第二區"
    })

    df.to_csv(LOCAL_FILE, index=False, encoding="utf-8-sig")
    print(f"✅ 已更新 {len(df)} 期資料")


# =========================
# 載入歷史號碼
# =========================

def load_numbers():
    df = pd.read_csv(LOCAL_FILE)

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
# 軟機率分布（不是亂數）
# =========================

def softmax(scores):
    if not scores:
        return {}

    m = max(scores.values())
    exps = {k: math.exp(v - m) for k, v in scores.items()}
    total = sum(exps.values())
    return {k: exps[k] / total for k in exps}


def weighted_pick(prob_map, k):
    nums = list(prob_map.keys())
    weights = list(prob_map.values())
    return random.choices(nums, weights=weights, k=k)


# =========================
# API：統計資料
# =========================

@app.route("/stats")
def stats():
    nums, _ = load_numbers()
    counter = Counter(nums)

    result = []
    for i in range(1, 39):
        result.append({
            "num": i,
            "count": counter.get(i, 0)
        })

    return jsonify(result)


# =========================
# API：預測
# =========================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    nums, specials = load_numbers()

    counter = Counter(nums)

    scores = {}

    for n in range(1, 39):
        scores[n] = counter.get(n, 0)

    probs = softmax(scores)

    if not probs:
        return jsonify({"error": "資料不足"}), 500

    if strategy == "hot":
        selected = sorted(counter, key=counter.get, reverse=True)[:6]

    elif strategy == "cold":
        selected = sorted(counter, key=counter.get)[:6]

    else:
        selected = sorted(set(weighted_pick(probs, 6)))

        while len(selected) < 6:
            selected.add(weighted_pick(probs, 1)[0])
        selected = sorted(selected)

    second_zone = Counter(specials).most_common(1)[0][0]

    return jsonify({
        "first_zone": selected,
        "second_zone": second_zone
    })


# =========================
# 啟動
# =========================

if __name__ == "__main__":
    sync_latest()
    app.run(host="0.0.0.0", port=10000)
