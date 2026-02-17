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
st.title("⚡ 威力彩高速機率最佳化模型")

# ===== 機率分布 =====
zone1 = df[[f"獎號{i}" for i in range(1,7)]].values.flatten()
counter1 = Counter(zone1)

nums1 = np.arange(1,39)
prob1 = np.array([counter1.get(n,0) for n in nums1])
prob1 = prob1 / prob1.sum()

counter2 = Counter(df["第二區"])
nums2 = np.array(list(counter2.keys()))
prob2 = np.array(list(counter2.values()))
prob2 = prob2 / prob2.sum()

# ===== 期望值計算（無模擬）=====
def expected_score(ticket):
    t1, t2 = ticket
    exp1 = sum(prob1[n-1] for n in t1)
    exp2 = prob2[list(nums2).index(t2)] * 2
    return exp1 + exp2

# ===== 搜尋 =====
best = []

for _ in range(3000):
    t1 = set(np.random.choice(nums1, 6, replace=False, p=prob1))
    t2 = np.random.choice(nums2, p=prob2)
    s = expected_score((t1, t2))
    best.append((s, t1, t2))

best = sorted(best, reverse=True)[:5]

# ===== 顯示 =====
rows = []
for i,(s,t1,t2) in enumerate(best,1):
    rows.append({
        "排名": i,
        "第一區": " ".join(map(str,sorted(t1))),
        "第二區": t2,
        "期望分數": round(s,4)
    })

st.table(pd.DataFrame(rows))

# ===== 機率圖 =====
fig, ax = plt.subplots(figsize=(12,4))
ax.bar(nums1, prob1, color="#22c55e")
ax.set_title("第一區機率權重分布")
ax.grid(alpha=0.3)
st.pyplot(fig)
