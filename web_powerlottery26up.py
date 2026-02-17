import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import random
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="威力彩預測引擎 2026", layout="wide")
st.title("🎯 威力彩專業預測引擎")

CSV_PATH = r"C:\Users\Super\Desktop\weli\weli_20260.csv"
df = pd.read_csv(CSV_PATH)

# ================= 控制面板 =================
st.sidebar.header("📈 策略設定")

recent_n = st.sidebar.slider(
    "近期期數權重",
    min_value=3,
    max_value=len(df),
    value=min(10, len(df))
)

hot_ratio = st.sidebar.slider(
    "熱號比例",
    min_value=0.2,
    max_value=0.8,
    value=0.5
)

# ================= 第一區動能 =================
recent_df = df.tail(recent_n)
zone1_recent = recent_df[["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]].values.flatten()

c1 = Counter(zone1_recent)

nums1 = list(range(1,39))
weights1 = np.array([c1.get(n, 0)+1 for n in nums1])

z1_df = pd.DataFrame({
    "號碼": nums1,
    "近期權重": weights1
})

z1_df["機率"] = z1_df["近期權重"] / z1_df["近期權重"].sum()
z1_df = z1_df.sort_values("機率", ascending=False)

st.subheader("📊 第一區近期動能排行")
st.dataframe(z1_df)

fig, ax = plt.subplots(figsize=(12,4))
ax.bar(z1_df["號碼"], z1_df["近期權重"], color="#38bdf8")
ax.set_title("第一區近期動能熱度")
ax.grid(alpha=0.3)
st.pyplot(fig)

# ================= 第二區動能 =================
c2 = Counter(recent_df["第二區"])
nums2 = sorted(c2.keys())
weights2 = [c2[n] for n in nums2]

z2_df = pd.DataFrame({
    "號碼": nums2,
    "近期權重": weights2
})

z2_df["機率"] = z2_df["近期權重"] / z2_df["近期權重"].sum()

st.subheader("🎯 第二區近期動能")
st.dataframe(z2_df)

fig2, ax2 = plt.subplots(figsize=(6,3))
ax2.bar(z2_df["號碼"], z2_df["近期權重"], color="#22d3ee")
ax2.set_title("第二區近期熱度")
ax2.grid(alpha=0.3)
st.pyplot(fig2)

# ================= 熱冷分組 =================
hot_count = int(6 * hot_ratio)

hot_nums = z1_df["號碼"].head(15).tolist()
cold_nums = z1_df["號碼"].tail(23).tolist()

# ================= 策略推薦 =================
st.subheader("🎲 策略推薦組合（熱冷平衡＋第二區）")

result_table = []

for i in range(1, 6):
    pick_hot = random.sample(hot_nums, hot_count)
    pick_cold = random.sample(cold_nums, 6 - hot_count)
    first_zone = sorted(pick_hot + pick_cold)

    second_zone = random.choices(nums2, weights=weights2, k=1)[0]

    result_table.append({
        "組合": f"第{i}",
        "第一區": " ".join(map(str, first_zone)),
        "第二區": second_zone
    })

st.table(pd.DataFrame(result_table))

# ================= 簡易命中模擬 =================
st.subheader("📊 隨機命中基準（參考值）")

def simulate_random():
    total = 0
    for _, row in df.iterrows():
        draw = {row[f"獎號{i}"] for i in range(1,7)}
        pred = set(random.sample(nums1, 6))
        total += len(draw & pred)
    return total / len(df)

st.write("🎯 平均命中球數：", round(simulate_random(), 2))
