from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter

app = Flask(__name__)

DATA_FILE = "weli_latest.csv"

# ==========================
# 🔄 自動更新資料
# ==========================
def update_data():
    try:
        print("📡 嘗試同步穩定資料源...")

       url = "https://raw.githubusercontent.com/ycshih/taiwan-lottery-datasets/master/data/powerlotto.csv"
        df = pd.read_csv(url)

        df = df[[
            "draw_date",
            "num1","num2","num3","num4","num5","num6","special"
        ]]

        df.columns = [
            "date","獎號1","獎號2","獎號3","獎號4","獎號5","獎號6","第二區"
        ]

        df.to_csv(DATA_FILE, index=False)

        print(f"✅ 成功更新 {len(df)} 期資料")

    except Exception as e:
        print("❌ 更新失敗:", e)

# ==========================
# 📊 讀取號碼
# ==========================
def load_numbers():
    df = pd.read_csv(DATA_FILE)
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    return nums

# ==========================
# 🎯 預測
# ==========================
@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "random")

    nums = load_numbers()
    counter = Counter(nums)

    if strategy == "hot":
        sorted_nums = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        picks = [n for n, _ in sorted_nums[:6]]

    elif strategy == "cold":
        sorted_nums = sorted(counter.items(), key=lambda x: x[1])
        picks = [n for n, _ in sorted_nums[:6]]

    else:
        picks = random.sample(range(1,39),6)

    picks.sort()
    special = random.randint(1,8)

    return jsonify({
        "first_zone": picks,
        "second_zone": special
    })

# ==========================
# 📊 統計
# ==========================
@app.route("/stats")
def stats():
    nums = load_numbers()
    counter = Counter(nums)

    result = []
    for i in range(1,39):
        result.append({
            "num": i,
            "count": counter.get(i, 0)
        })

    return jsonify(result)

@app.route("/")
def home():
    return "Power Lottery AI API running with stable data source"

# ==========================
# 🚀 啟動
# ==========================
if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=10000)
