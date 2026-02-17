import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import random
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="威力彩雙區策略引擎", layout="wide")
st.title("🎯 威力彩雙區策略回測系統")

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"
df = pd.read_csv(CSV_PATH)

# ===== 第一區統計 =====
zone1 = df[[f"獎號{i}" for i in range(1,7)]].values.flatten()
counter1 = Counter(zone1)

nums1 = list(range(1,39))
freq1 = np.array([counter1.get(n,0)+1 for n in nums1])

rank1 = pd.DataFrame({
    "號碼": nums1,
    "次數": freq1
}).sort_values("次數", ascending=False)

# ===== 第二區統計 =====
counter2 = Counter(df["第二區"])
nums2 = sorted(counter2.keys())
freq2 = [counter2[n] for n in nums2]

# ===== 策略池 =====
hot1 = rank1["號碼"].head(15).tolist()
cold1 = rank1["號碼"].tail(23).tolist()

def strategy_hot():
    return set(random.sample(hot1,6)), random.choice(nums2)

def strategy_cold():
    return set(random.sample(cold1,6)), random.choice(nums2)

def strategy_mix():
    return set(random.sample(hot1,3)+random.sample(cold1,3)), random.choice(nums2)

def strategy_random():
    return set(random.sample(nums1,6)), random.choice(nums2)

strategies = {
    "🔥 熱號派": strategy_hot,
    "🧊 冷號派": strategy_cold,
    "⚖ 熱冷混合": strategy_mix,
    "🎲 純隨機": strategy_random
}

# ===== 回測 =====
def evaluate(strategy_func):
    scores = []
    for _, row in df.iterrows():
        draw1 = {row[f"獎號{i}"] for i in range(1,7)}
        draw2 = row["第二區"]

        pred1, pred2 = strategy_func()

        hit1 = len(draw1 & pred1)
        hit2 = 1 if pred2 == draw2 else 0

        score = hit1 + hit2*2  # 第二區加權2分
        scores.append(score)

    return np.mean(scores), scores

results = {}
curves = {}

for name, func in strategies.items():
    avg, history = evaluate(func)
    results[name] = avg
    curves[name] = history

result_df = pd.DataFrame({
    "策略": list(results.keys()),
    "平均綜合得分": list(results.values())
}).sort_values("平均綜合得分", ascending=False)

st.subheader("📊 雙區策略比較")
st.dataframe(result_df)

best_strategy = result_df.iloc[0]["策略"]
st.success(f"🎯 目前最佳雙區策略： {best_strategy}")

# ===== 曲線 =====
st.subheader("📈 綜合命中趨勢")

fig, ax = plt.subplots(figsize=(12,5))

for name, history in curves.items():
    ma = np.convolve(history, np.ones(5)/5, mode="valid")
    ax.plot(ma, label=name)

ax.set_title("雙區命中移動平均")
ax.legend()
ax.grid(alpha=0.3)

st.pyplot(fig)

# ===== 推薦 =====
st.subheader("🎲 最佳策略推薦")

best_func = strategies[best_strategy]

table = []
for i in range(1,6):
    p1, p2 = best_func()
    table.append({
        "組合": i,
        "第一區": " ".join(map(str, sorted(p1))),
        "第二區": p2
    })

st.table(pd.DataFrame(table).reset_index(drop=True))
