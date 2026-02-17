import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"
df = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="威力彩 AI 預測引擎", layout="wide")
st.title("🤖 威力彩 AI 時序預測系統")

# ===== 建立轉移機率模型（第一區） =====
transitions = defaultdict(Counter)

for i in range(len(df)-1):
    prev_nums = df.iloc[i][[f"獎號{j}" for j in range(1,7)]]
    next_nums = df.iloc[i+1][[f"獎號{j}" for j in range(1,7)]]
    for p in prev_nums:
        for n in next_nums:
            transitions[p][n] += 1

def ai_pick_zone1():
    pool = []
    keys = list(transitions.keys())
    current = random.choice(keys)

    for _ in range(6):
        nexts = transitions[current]
        if not nexts:
            current = random.choice(keys)
        else:
            nums = list(nexts.keys())
            weights = list(nexts.values())
            current = random.choices(nums, weights=weights, k=1)[0]
        pool.append(current)

    return sorted(set(pool))[:6]

# ===== 第二區機率 =====
z2_counter = Counter(df["第二區"])
z2_nums = list(z2_counter.keys())
z2_weights = list(z2_counter.values())

def ai_pick_zone2():
    return random.choices(z2_nums, weights=z2_weights, k=1)[0]

# ===== AI推薦 =====
st.subheader("🎯 AI 預測推薦組合")

table = []

for i in range(1,6):
    z1 = ai_pick_zone1()
    z2 = ai_pick_zone2()
    table.append({
        "組合": i,
        "第一區": " ".join(map(str, z1)),
        "第二區": z2
    })

st.table(pd.DataFrame(table))

# ===== 機率熱度圖 =====
all_nums = range(1,39)
freq = Counter(df[[f"獎號{i}" for i in range(1,7)]].values.flatten())

heat = [freq.get(n,0) for n in all_nums]

fig, ax = plt.subplots(figsize=(12,4))
ax.bar(all_nums, heat, color="#f97316")
ax.set_title("AI 學習後號碼熱度分布")
ax.grid(alpha=0.3)
st.pyplot(fig)
