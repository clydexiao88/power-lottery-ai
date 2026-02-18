from flask import Flask, jsonify, request
import pandas as pd
import requests
import random
from collections import Counter

app = Flask(__name__)

DATA_FILE = "weli_latest.csv"

# ============================
# 🔄 從官方 API 同步資料
# ============================

def update_data():
    try:
        print("📡 同步穩定歷史資料庫...")

        url = "https://raw.githubusercontent.com/kiang/taiwan-lottery-history/master/data/powerlotto.csv"
        df = pd.read_csv(url)

        df = df.rename(columns={
            "n1": "獎號1",
            "n2": "獎號2",
            "n3": "獎號3",
            "n4": "獎號4",
            "n5": "獎號5",
            "n6": "獎號6",
            "sp": "第二區"
        })

        df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6","第二區"]].to_csv(
            "weli_latest.csv", index=False
        )

        print("✅ 成功更新", len(df), "期")

    except Exception as e:
        print("❌ 更新失敗:", e)



# ============================
# 📊 讀取所有號碼
# ============================

def load_numbers():
    df = pd.read_csv(DATA_FILE)
    return df


# ============================
# 🎯 預測 API
# ============================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "random")

    df = load_numbers()
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    counter = Counter(nums)

    if strategy == "hot":
        ranked = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        picks = [n for n, _ in ranked[:6]]

    elif strategy == "cold":
        ranked = sorted(counter.items(), key=lambda x: x[1])
        picks = [n for n, _ in ranked[:6]]

    else:
        picks = random.sample(range(1, 39), 6)

    picks.sort()
    special = random.randint(1, 8)

    return jsonify({
        "first_zone": picks,
        "second_zone": special
    })


# ============================
# 📈 統計 API
# ============================

@app.route("/stats")
def stats():
    df = load_numbers()
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    counter = Counter(nums)

    result = []
    for i in range(1, 39):
        result.append({
            "num": i,
            "count": counter.get(i, 0)
        })

    return jsonify(result)


# ============================
# 🏠 首頁測試
# ============================

@app.route("/")
def home():
    return "Power Lottery AI API running with official data source"


# ============================
# 🚀 啟動
# ============================

if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=10000)
