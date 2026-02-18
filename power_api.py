from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import random
from collections import Counter
import os

app = Flask(__name__)
CORS(app)

# ===== 讀取 CSV =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "weli_20260.csv")

df = pd.read_csv(CSV_PATH)

zone_cols = ["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]

nums = df[zone_cols].values.flatten().tolist()

counter = Counter(nums)

ALL_NUMS = list(range(1,39))

# ===== 工具 =====

def unique_sample(pool, k):
    pool = list(set(pool))
    return sorted(random.sample(pool, k))


# ===== 策略 =====

def ai_strategy():
    weighted = []
    for n in ALL_NUMS:
        weighted += [n] * max(counter.get(n,1),1)
    return unique_sample(weighted, 6)

def hot_strategy():
    hot = [n for n,_ in counter.most_common(18)]
    return unique_sample(hot,6)

def cold_strategy():
    cold = [n for n,_ in counter.most_common()[-18:]]
    return unique_sample(cold,6)

def random_strategy():
    return unique_sample(ALL_NUMS,6)


# ===== API =====

@app.route("/")
def home():
    return "Power Lottery AI API running with real CSV data"

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy","ai")

    if strategy == "ai":
        nums = ai_strategy()
    elif strategy == "hot":
        nums = hot_strategy()
    elif strategy == "cold":
        nums = cold_strategy()
    else:
        nums = random_strategy()

    second_zone = random.randint(1,8)

    return jsonify({
        "first_zone": nums,
        "second_zone": second_zone
    })

@app.route("/stats")
def stats():
    return jsonify([
        {"num":i,"count":counter.get(i,0)}
        for i in ALL_NUMS
    ])

# ===== 雲端啟動 =====

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
