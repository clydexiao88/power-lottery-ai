from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import os

app = Flask(__name__)

DATA_FILE = "weli_latest.csv"


# 如果沒有資料就用你原本 CSV 當初始資料
def ensure_data():
    if not os.path.exists(DATA_FILE):
        print("⚠ 尚未有自動資料庫，使用初始 CSV")
        pd.read_csv("weli_20260.csv", encoding="cp950").to_csv(DATA_FILE, index=False)


def load_nums():
    df = pd.read_csv(DATA_FILE)
    nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
    return nums.tolist()


@app.route("/")
def home():
    return "Power Lottery AI API running"


@app.route("/stats")
def stats():
    nums = load_nums()
    counter = Counter(nums)

    return jsonify([
        {"num": i, "count": counter.get(i, 0)}
        for i in range(1, 39)
    ])


@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "random")

    nums = load_nums()
    counter = Counter(nums)

    pool = list(range(1, 39))

    if strategy == "hot":
        pool = sorted(pool, key=lambda x: counter.get(x, 0), reverse=True)

    elif strategy == "cold":
        pool = sorted(pool, key=lambda x: counter.get(x, 0))

    picks = random.sample(pool[:20], 6)
    second = random.randint(1, 8)

    return jsonify({
        "first_zone": sorted(picks),
        "second_zone": second
    })


if __name__ == "__main__":
    ensure_data()
    app.run(host="0.0.0.0", port=10000)
