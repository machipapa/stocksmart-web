import streamlit as st
import pandas as pd
import yfinance as yf

st.title("📊 StockSmart PRO - 複数銘柄スクリーニング")

# CSVファイル読み込み
try:
    stocks_df = pd.read_csv("stocks_list_sample.csv")
except FileNotFoundError:
    st.error("❌ stocks_list_sample.csv が見つかりません。アップロードしてください。")
    st.stop()

# 検索入力欄
search_term = st.text_input("🔍 銘柄名またはコードで検索", "").strip()

# スコア付けロジック
results = []

for i, row in stocks_df.iterrows():
    code = row["銘柄コード"]
    name = row["銘柄名"]

    try:
        ticker = yf.Ticker(code)
        info = ticker.info

        per = info.get("trailingPE", None)
        volume = info.get("volume", 0)
        average_volume = info.get("averageVolume", 1)

        score = 0
        if per and 5 <= per <= 15:
            score += 1
        if average_volume and volume > average_volume * 1.5:
            score += 1
        # 3点目以降はデモのため仮にランダムや仮設定で省略可能

        results.append({
            "銘柄コード": code,
            "銘柄名": name,
            "PER": per,
            "出来高": volume,
            "スコア": score
        })

    except Exception as e:
        st.warning(f"{name}（{code}）：データ取得に失敗しました")

# 結果をDataFrame化
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="スコア", ascending=False)

# フィルター適用
if search_term:
    results_df = results_df[results_df["銘柄名"].str.contains(search_term, case=False, na=False) |
                            results_df["銘柄コード"].str.contains(search_term)]

# 表示
if not results_df.empty:
    st.dataframe(results_df)
else:
    st.warning("条件に一致する銘柄がありませんでした。")
