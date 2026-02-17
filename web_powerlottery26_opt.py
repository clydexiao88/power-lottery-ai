import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import random
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"
df = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="威力彩機率最佳化引擎", layout="wide")
st.title("📈 威力彩機率最佳化投注模型")

# ===== 機率分布 =====
zone1_nums = df[[f"獎號{i}" for i in range(1,7)]].values.flatten()
counter1 = Counter(zone1_nums)

nums1 = np.arange(1,39)
prob1 = np.array([counter1.get(n,0) for n in nums1])
prob1 = prob1 / prob1.sum()

counter2 = Counter(df["第二區"])
nums2 = np.array(list(counter2.keys()))
prob2 = np.array(list(counter2.values()))
prob2 = prob2 / prob2.sum()

# ===== 模擬開獎 =====
def simulate_draw():
    z1 = set(np.random.choice(nums1, 6, replace=False, p=prob1))
    z2 = np.random.choice(nums2, p=prob2)
    return z1, z2

# ===== 評分函數 =====
def score(ticket, sims=5000):
    total = 0
    for _ in range(sims):
        draw1, draw2 = simulate_draw()
        hit1 = len(draw1 & ticket[0])
        hit2 = 1 if draw2 == ticket[1] else 0
        total += hit1 + hit2*2
    return total / sims

# ===== 搜尋最佳組合 =====
st.subheader("🔍 機率搜尋最佳組合中（請稍等）")

best = []

for _ in range(200):
    t1 = set(np.random.choice(nums1, 6, replace=False, p=prob1))
    t2 = np.random.choice(nums2, p=prob2)
    s = score((t1,t2), sims=2000)
    best.append((s, t1, t2))

best = sorted(best, reverse=True)[:5]

# ===== 顯示 =====
result = []

for i,(s,t1,t2) in enumerate(best,1):
    result.append({
        "排名": i,
        "第一區": " ".join(map(str,sorted(t1))),
        "第二區": t2,
        "期望命中分數": round(s,3)
    })

st.table(pd.DataFrame(result))

# ===== 視覺化機率 =====
fig, ax = plt.subplots(figsize=(12,4))
ax.bar(nums1, prob1, color="#22c55e")
ax.set_title("第一區機率分布")
ax.grid(alpha=0.3)
st.pyplot(fig)
