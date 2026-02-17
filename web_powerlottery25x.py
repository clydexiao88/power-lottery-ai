import streamlit as st
import pandas as pd
import random
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="威力彩智慧分析", layout="wide")
st.title("🎯 威力彩數據分析系統")

CSV_PATH = r"C:\Users\Super\Desktop\PyDesktop\weli_2025.csv"

df = pd.read_csv(CSV_PATH)

zone1_cols = ["獎號1","獎號2","獎號3","獎號4","獎號5","獎號6"]
zone2_col = "第二區"

def weighted_sample(nums, weights, k):
    pool = [(n,w) for n,w in zip(nums, weights) if w > 0]
    chosen = []

    for _ in range(min(k, len(pool))):
        total = sum(w for _,w in pool)
        r = random.uniform(0, total)
        upto = 0
        for i,(n,w) in enumerate(pool):
            upto += w
            if upto >= r:
                chosen.append(n)
                pool.pop(i)
                break
    return chosen

def analyze():
    zone1_nums=[]
    zone2_nums=[]

    for _,row in df.iterrows():
        for c in zone1_cols:
            zone1_nums.append(int(row[c]))
        zone2_nums.append(int(row[zone2_col]))

    c1 = Counter(zone1_nums)
    c2 = Counter(zone2_nums)

    z1_df = pd.DataFrame(sorted(c1.items()), columns=["號碼","次數"])
    z1_df["機率"] = z1_df["次數"] / z1_df["次數"].sum()

    z2_df = pd.DataFrame(sorted(c2.items()), columns=["號碼","次數"])
    z2_df["機率"] = z2_df["次數"] / z2_df["次數"].sum()

    st.subheader("🔥 第一區號碼機率")
    st.dataframe(z1_df.sort_values("機率", ascending=False))

    st.subheader("🎯 第二區號碼機率")
    st.dataframe(z2_df.sort_values("機率", ascending=False))

    fig1, ax1 = plt.subplots()
    ax1.bar(z1_df["號碼"], z1_df["次數"])
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(z2_df["號碼"], z2_df["次數"])
    st.pyplot(fig2)

    st.subheader("🎲 智慧推薦組合")

    for _ in range(5):
        pick1 = weighted_sample(z1_df["號碼"].tolist(), z1_df["次數"].tolist(), 6)
        pick2 = weighted_sample(z2_df["號碼"].tolist(), z2_df["次數"].tolist(), 1)[0]
        st.write(f"第一區：{sorted(pick1)} ｜ 第二區：{pick2}")

if st.button("🚀 一鍵分析威力彩"):
    analyze()
