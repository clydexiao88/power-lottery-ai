from flask import Flask, jsonify, request
import pandas as pd
import random
from collections import Counter
import math
import requests
from io import StringIO
import os

app = Flask(__name__)

HISTORY_FILE = "weli_history.csv"
LATEST_FILE = "weli_latest.csv"

# 穩定開源歷史資料源（長期可用）
DATA_URL = "https://raw.githubusercontent.com/ycshih/taiwan-lottery-datasets/master/data/powerlotto.csv"


# =========================
# 同步完整歷史資料
# =========================

def sync_latest():
    if os.path.exists(HISTORY_FILE):
        print("✅ 已有本地歷史資料庫，略過下載")
        return

    print("📡 下載完整歷史資料庫中...")

    r = requests.get(DATA_URL, timeout=30)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text))

    # 官方欄位格式轉換
    df = df.rename(columns={
        "draw_date": "開獎日期",
        "num1": "獎號1",
        "num2": "獎號2",
        "num3": "獎號3",
        "num4": "獎號4",
        "num5": "獎號5",
        "num6": "獎號6",
        "special_num": "第二區"
    })

    df = df[[
        "開獎日期",
        "獎號1","獎號2","獎號3",
        "獎號4","獎號5","獎號6",
        "第二區"
    ]]

    df.to_csv(HISTORY_FILE, index=False, encoding="utf-8-sig")
    df.tail(100).to_csv(LATEST_FILE, index=False, encoding="utf-8-sig")

    print(f"✅ 歷史期數：{len(df)}")
    print("🔥 最近100期同步完成")


# =========================
# 讀取資料
# =========================

def load_numbers(use_latest=True):
    file = LATEST_FILE if use_latest else HISTORY_FILE
    df = pd.read_csv(file)

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
    nums, _ = load_numbers(True)
    c = Counter(nums)
    return jsonify([{"num": i, "count": c.get(i, 0)} for i in range(1, 39)])


# =========================
# AI 預測 API
# =========================

@app.route("/predict")
def predict():
    strategy = request.args.get("strategy", "ai")

    recent, specials = load_numbers(True)
    history, _ = load_numbers(False)

    r_c = Counter(recent)
    h_c = Counter(history)

    scores = {}
    for i in range(1, 39):
        scores[i] = r_c.get(i, 0) * 1.7 + h_c.get(i, 0) * 0.3

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
