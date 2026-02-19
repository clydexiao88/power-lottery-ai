import pandas as pd

SOURCE = "weli_20260.csv"   # 你現在手動整理那份
TARGET = "weli_latest.csv"

df = pd.read_csv(SOURCE)

df.to_csv(TARGET, index=False)

print("✅ 已同步到主資料庫 weli_latest.csv")
