import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import random
import os

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"

st.set_page_config(page_title="威力彩即時分析", layout="wide")
st.title("🎯 威力彩即時數據分析（CSV即時同步）")

# === 永遠即時讀 CSV ===
if not os.path.exists(CSV_PATH):
    st.error("找不到 CSV 檔案")
    st.stop()

df = pd.read_csv(CSV_PATH).dropna(how="all")

st.caption(f"📂 目前資料筆數：{len(df)}（存檔後自動更新）")

# ========= 第一區 =========
zone1 = df[[f"獎號{i}" for i in range(1,7)]].values.flatten()
counter1 = Counter(zone1)

z1_df = pd.DataFrame(sorted(counter1.items()), columns=["號碼","次數"])
z1_df["機率"] = z1_df["次數"] / z1_df["次數"].sum()

st.subheader("📊 第一區統計")
st.dataframe(z1_df)

fig1, ax1 = plt.subplots(figsize=(12,4))
ax1.bar(z1_df["號碼"], z1_df["次數"], color="#60a5fa")
ax1.set_title("第一區熱度分布")
ax1.grid(alpha=0.3)
st.pyplot(fig1)

# ========= 第二區 =========
counter2 = Counter(df["第二區"])
z2_df = pd.DataFrame(sorted(counter2.items()), columns=["號碼","次數"])
z2_df["機率"] = z2_df["次數"] / z2_df["次數"].sum()

st.subheader("🎯 第二區統計")
st.dataframe(z2_df)

fig2, ax2 = plt.subplots(figsize=(6,3))
ax2.bar(z2_df["號碼"], z2_df["次數"], color="#34d399")
ax2.set_title("第二區熱度")
ax2.grid(alpha=0.3)
st.pyplot(fig2)

# ========= 即時推薦 =========
st.subheader("🎲 即時推薦組合")

nums1 = z1_df["號碼"].tolist()
weights1 = z1_df["次數"].tolist()
nums2 = z2_df["號碼"].tolist()
weights2 = z2_df["次數"].tolist()

for i in range(1,6):
    first = random.choices(nums1, weights=weights1, k=6)
    second = random.choices(nums2, weights=weights2, k=1)[0]
    st.write(f"第{i}組：第一區 {sorted(set(first))} ｜ 第二區 {second}")
