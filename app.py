import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 株価チャート & 優良株スクリーニング")

# 銘柄リストの読み込み（10銘柄または全銘柄CSV）
@st.cache_data
def load_tickers():
    df = pd.read_csv("stocks_list_sample.csv")  # 「銘柄コード,会社名」の形式
    return df

tickers_df = load_tickers()
ticker_names = [f"{row['会社名']}（{row['銘柄コード']}）" for _, row in tickers_df.iterrows()]

# 銘柄選択
selected = st.selectbox("🔍 銘柄を選択", ticker_names)
ticker_code = selected.split("（")[-1].replace("）", "")

# 時間足選択
timeframe = st.selectbox("⏰ 時間足を選択", [
    "1時間足", "4時間足", "日足", "週足", "月足"
])

# 時間足マップ
interval_map = {
    "1時間足": ("30d", "1h"),
    "4時間足": ("7d", "1h"),
    "日足":    ("6mo", "1d"),
    "週足":    ("1y", "1wk"),
    "月足":    ("5y", "1mo"),
}

# データ取得
period, interval = interval_map[timeframe]
ticker = yf.Ticker(ticker_code)
df = ticker.history(period=period, interval=interval)

if timeframe == "4時間足":
    df = df.resample("4H").agg({
        "Open": "first", "High": "max", "Low": "min",
        "Close": "last", "Volume": "sum"
    }).dropna()

if df.empty:
    st.error("📛 データが取得できませんでした。")
else:
    df["13MA"] = df["Close"].rolling(window=13).mean()
    df["26MA"] = df["Close"].rolling(window=26).mean()

    # トレンド判定
    trend = "判定不可"
    if df["13MA"].iloc[-1] > df["26MA"].iloc[-1]:
        trend = "上昇トレンド"
    elif df["13MA"].iloc[-1] < df["26MA"].iloc[-1]:
        trend = "下降トレンド"
    else:
        trend = "横ばい"

    # チャート描画
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color='blue',
        decreasing_line_color='red',
        name="ローソク足"
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df['13MA'],
        line=dict(color="yellow", width=1), name="13MA"
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df['26MA'],
        line=dict(color="white", width=1), name="26MA"
    ))

    fig.update_layout(
        title=f"{selected}（{timeframe}） - {trend}",
        xaxis_title="日付", yaxis_title="",  # "価格"だけ消して数字は表示
        plot_bgcolor="black", paper_bgcolor="black",
        font_color="white", height=600,
        xaxis_rangeslider_visible=True,
        xaxis=dict(domain=[0, 0.85]),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5, font=dict(size=12)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # スコア算出（簡易版）
    score = 0
    explain = []

    # 1. 移動平均ゴールデンクロス
    if df["13MA"].iloc[-1] > df["26MA"].iloc[-1]:
        score += 5
        explain.append("✅ ゴールデンクロス（+5）")
    else:
        explain.append("⚠️ デッドクロス")

    # 2. 出来高上昇
    avg_volume = df["Volume"].rolling(5).mean().iloc[-1]
    if df["Volume"].iloc[-1] > avg_volume:
        score += 5
        explain.append("✅ 出来高増（+5）")
    else:
        explain.append("⚠️ 出来高横ばい")

    # 3. PER（仮設定）
    try:
        per = ticker.info.get("trailingPE", None)
        if per and 10 <= per <= 20:
            score += 5
            explain.append(f"✅ PER適正: {per:.1f}（+5）")
        else:
            explain.append(f"⚠️ PER不適正: {per}")
    except:
        explain.append("⚠️ PER取得失敗")

    # 4. 業績
    try:
        eps = ticker.info.get("trailingEps", None)
        if eps and eps > 0:
            score += 5
            explain.append(f"✅ EPS黒字: {eps:.2f}（+5）")
        else:
            explain.append("⚠️ EPS赤字")
    except:
        explain.append("⚠️ EPS取得失敗")

    # 5. トレンド
    if trend == "上昇トレンド":
        score += 5
        explain.append("✅ トレンド上昇（+5）")
    else:
        explain.append("⚠️ トレンド弱い")

    st.subheader(f"📊 総合スコア: {score} / 25")
    st.markdown("・" + "\n・".join(explain))
