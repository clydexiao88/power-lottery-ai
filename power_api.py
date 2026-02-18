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
        print("📡 從政府開放資料更新...")

        csv_url = "https://quality.data.gov.tw/dq_download_csv.php?nid=5961"

        res = requests.get(csv_url, timeout=20)
        res.raise_for_status()

        df = pd.read_csv(io.StringIO(res.text))

        print("📋 真實欄位名稱：")
        print(df.columns.tolist())

        # 自動抓包含「獎號」的欄位
        number_cols = [c for c in df.columns if "獎號" in c]

        if len(number_cols) < 6:
            raise Exception("找不到足夠獎號欄位")

        second_col = [c for c in df.columns if "第二區" in c or "特別" in c]

        if not second_col:
            raise Exception("找不到第二區欄位")

        new_df = df[number_cols[:6]].copy()
        new_df["第二區"] = df[second_col[0]]

        new_df.to_csv(DATA_FILE, index=False)

        print("✅ 成功更新", len(new_df), "期")

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
