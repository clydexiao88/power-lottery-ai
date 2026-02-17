from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter

app = Flask(__name__)

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"


# ---------------------------
# 載入第一區號碼
# ---------------------------
def load_nums():
    df = pd.read_csv(CSV_PATH)

    cols = ["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]
    nums = df[cols].values.flatten().tolist()

    return [int(n) for n in nums if not pd.isna(n)]


# ---------------------------
# AI 加權選號
# ---------------------------
def weighted_pick(nums):
    counter = Counter(nums)

    numbers = list(counter.keys())
    weights = list(counter.values())

    picks = set()
    while len(picks) < 6:
        picks.add(random.choices(numbers, weights=weights, k=1)[0])

    return sorted(picks)


# ---------------------------
# 熱號策略（出現最多）
# ---------------------------
def hot_pick(nums):
    counter = Counter(nums)
    hottest = counter.most_common(6)
    return sorted([n for n, _ in hottest])


# ---------------------------
# 冷號策略（出現最少）
# ---------------------------
def cold_pick(nums):
    counter = Counter(nums)
    coldest = sorted(counter.items(), key=lambda x: x[1])[:6]
    return sorted([n for n, _ in coldest])


# ---------------------------
# 預測 API
# ---------------------------
@app.route("/predict")
def predict():
    try:
        strategy = request.args.get("strategy", "ai")

        nums = load_nums()

        if len(nums) == 0:
            return jsonify({"error": "CSV 無資料"})

        if strategy == "ai":
            first = weighted_pick(nums)
        elif strategy == "hot":
            first = hot_pick(nums)
        elif strategy == "cold":
            first = cold_pick(nums)
        else:
            first = weighted_pick(nums)

        second = random.randint(1, 8)

        return jsonify({
            "first_zone": first,
            "second_zone": second
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------------------
# 統計 API（圖表用）
# ---------------------------
@app.route("/stats")
def stats():
    try:
        nums = load_nums()
        counter = Counter(nums)

        result = []
        for i in range(1, 39):
            result.append({
                "num": i,
                "count": counter.get(i, 0)
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------------------
# 啟動
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
