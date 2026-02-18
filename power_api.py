from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import requests
import io

app = Flask(__name__)

DATA_FILE = "weli_latest.csv"

# =========================
# 🔄 政府開放資料更新
# =========================

def update_data():
    try:
        print("📡 同步官方穩定歷史資料庫...")

        url = "https://raw.githubusercontent.com/ycshih/taiwan-lottery-datasets/main/data/powerlotto.csv"

        df = pd.read_csv(url)

        df = df.rename(columns={
            "num1": "獎號1",
            "num2": "獎號2",
            "num3": "獎號3",
            "num4": "獎號4",
            "num5": "獎號5",
            "num6": "獎號6",
            "special": "第二區"
        })

        df[[
            "獎號1",
            "獎號2",
            "獎號3",
            "獎號4",
            "獎號5",
            "獎號6",
            "第二區"
        ]].to_csv("weli_latest.csv", index=False)

        print(f"✅ 更新完成：{len(df)} 期資料")

    except Exception as e:
        print("❌ 更新失敗:", e)


# =========================
# 📊 讀資料
# =========================

def load_numbers():
    return pd.read_csv(DATA_FILE)

# =========================
# 🎯 預測
# =========================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "random")

    df = load_numbers()
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    counter = Counter(nums)

    if strategy == "hot":
        picks = [n for n,_ in sorted(counter.items(), key=lambda x:x[1], reverse=True)[:6]]
    elif strategy == "cold":
        picks = [n for n,_ in sorted(counter.items(), key=lambda x:x[1])[:6]]
    else:
        picks = random.sample(range(1,39),6)

    picks.sort()
    return jsonify({
        "first_zone": picks,
        "second_zone": random.randint(1,8)
    })

# =========================
# 📈 統計
# =========================

@app.route("/stats")
def stats():
    df = load_numbers()
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    counter = Counter(nums)

    return jsonify([
        {"num": i, "count": counter.get(i,0)}
        for i in range(1,39)
    ])

@app.route("/")
def home():
    return "Power Lottery AI API running (official open data)"

# =========================

if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=10000)
