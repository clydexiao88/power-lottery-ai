import pandas as pd

# 穩定公開鏡像（官方資料同步）
CSV_URL = "https://raw.githubusercontent.com/ycchen0/lottery-data/main/powerlotto.csv"

OUTPUT_FILE = "weli_latest.csv"

def update_from_mirror():
    df = pd.read_csv(CSV_URL)

    # 只取威力彩號碼欄位
    df = df[["n1","n2","n3","n4","n5","n6","second"]]

    df.to_csv(OUTPUT_FILE, index=False)

    print("✅ 鏡像資料同步完成，共", len(df), "筆")

if __name__ == "__main__":
    update_from_mirror()
