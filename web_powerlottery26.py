import os
import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import random

# 中文字型修正
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="威力彩智慧分析 2026", layout="wide")
st.title("🎯 威力彩 2026 專業數據分析系統")

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"

@st.cache_data(show_spinner=False)
def load_data(path, last_modified):
    return pd.read_csv(path)

last_modified = os.path.getmtime(CSV_PATH)

df = load_data(CSV_PATH, last_modified)
# ================= 第一區 =================
zone1_nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()
c1 = Counter(zone1_nums)

z1_df = pd.DataFrame(sorted(c1.items()), columns=["號碼","次數"])
z1_df["機率"] = z1_df["次數"] / z1_df["次數"].sum()

hot1 = z1_df["次數"].quantile(0.75)
cold1 = z1_df["次數"].quantile(0.25)

colors1 = z1_df["次數"].apply(
    lambda x: "red" if x >= hot1 else "blue" if x <= cold1 else "#6b7280"
)

st.subheader("📊 第一區完整統計")
st.dataframe(z1_df)

fig1, ax1 = plt.subplots(figsize=(12,4))
ax1.bar(z1_df["號碼"], z1_df["次數"], color=colors1)

trend1 = z1_df["次數"].rolling(5, center=True).mean()
ax1.plot(z1_df["號碼"], trend1, color="#facc15", linewidth=3, label="趨勢線")

ax1.set_title("第一區熱度分布（紅=熱號｜藍=冷號）")
ax1.legend()
ax1.grid(alpha=0.3)
st.pyplot(fig1)

# ================= 第二區 =================
c2 = Counter(df["第二區"])

z2_df = pd.DataFrame(sorted(c2.items()), columns=["號碼","次數"])
z2_df["機率"] = z2_df["次數"] / z2_df["次數"].sum()

hot2 = z2_df["次數"].quantile(0.75)
cold2 = z2_df["次數"].quantile(0.25)

colors2 = z2_df["次數"].apply(
    lambda x: "red" if x >= hot2 else "blue" if x <= cold2 else "#6b7280"
)

st.subheader("🎯 第二區完整統計")
st.dataframe(z2_df)

fig2, ax2 = plt.subplots(figsize=(8,3))
ax2.bar(z2_df["號碼"], z2_df["次數"], color=colors2)

trend2 = z2_df["次數"].rolling(3, center=True).mean()
ax2.plot(z2_df["號碼"], trend2, color="#22d3ee", linewidth=2, label="趨勢線")

ax2.set_title("第二區熱度分布")
ax2.legend()
ax2.grid(alpha=0.3)
st.pyplot(fig2)

# ================= 智慧推薦 =================
def weighted_pick(nums, weights, k):
    pool = list(zip(nums, weights))
    picks = []
    for _ in range(min(k, len(pool))):
        total = sum(w for _, w in pool)
        r = random.uniform(0, total)
        upto = 0
        for i, (n, w) in enumerate(pool):
            upto += w
            if upto >= r:
                picks.append(n)
                pool.pop(i)
                break
    return picks

st.subheader("🎲 智慧推薦組合（熱度權重）")

nums1 = z1_df["號碼"].tolist()
w1 = z1_df["次數"].tolist()

nums2 = z2_df["號碼"].tolist()
w2 = z2_df["次數"].tolist()

for _ in range(5):
    first = weighted_pick(nums1, w1, 6)
    second = weighted_pick(nums2, w2, 1)[0]
    st.write(f"第一區：{sorted(first)} ｜ 第二區：{second}")
