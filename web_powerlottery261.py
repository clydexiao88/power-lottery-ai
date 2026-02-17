import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import random

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="威力彩智慧分析 2026", layout="wide")
st.title("🎯 威力彩 2026威力彩 原始數據分析系統")

CSV_PATH = r"C:\Users\Super\Desktop\PyDesktop\weli_20260.csv"

# === 讀取資料 ===
df = pd.read_csv(CSV_PATH)

#===st.write("📊 目前分析期數：", len(df))
#===st.write(df[["期別"]].tail())

# === 第一區標準統計（不可能漏）===
zone1_nums = df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()

counter1 = Counter(zone1_nums)

z1_df = pd.DataFrame(sorted(counter1.items()), columns=["號碼","出現次數"])
z1_df["機率"] = z1_df["出現次數"] / z1_df["出現次數"].sum()

st.subheader("🔥 第一區完整統計（驗證用）")
st.dataframe(z1_df)

# === 第二區統計 ===
counter2 = Counter(df["第二區"])
z2_df = pd.DataFrame(sorted(counter2.items()), columns=["號碼","出現次數"])
z2_df["機率"] = z2_df["出現次數"] / z2_df["出現次數"].sum()

st.subheader("🎯 第二區統計")
st.dataframe(z2_df)

# === 圖表 ===
fig1, ax1 = plt.subplots()
ax1.bar(z1_df["號碼"], z1_df["出現次數"])
ax1.set_title("第一區熱度分布")
st.pyplot(fig1)

# === 智慧推薦 ===
def weighted_pick(nums, weights, k):
    pool = list(zip(nums, weights))
    picks = []
    for _ in range(min(k, len(pool))):
        total = sum(w for _,w in pool)
        r = random.uniform(0, total)
        upto = 0
        for i,(n,w) in enumerate(pool):
            upto += w
            if upto >= r:
                picks.append(n)
                pool.pop(i)
                break
    return picks

st.subheader("🎲 智慧推薦組合")

nums1 = z1_df["號碼"].tolist()
weights1 = z1_df["出現次數"].tolist()

nums2 = z2_df["號碼"].tolist()
weights2 = z2_df["出現次數"].tolist()

for _ in range(5):
    first = weighted_pick(nums1, weights1, 6)
    second = weighted_pick(nums2, weights2, 1)[0]
    st.write(f"第一區：{sorted(first)} ｜ 第二區：{second}")
