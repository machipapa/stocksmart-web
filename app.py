import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
# スマホ画面対応（幅100%に調整）
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    .css-1cpxqw2 {
        max-width: 100% !important;
    }
    .stPlotlyChart {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 株価チャートビューワー")

# 銘柄コード入力
ticker_code = st.text_input("銘柄コードを入力（例：7203.T）", value="7203.T")

# 時間足選択
timeframe = st.selectbox("時間足を選択", [
    "1時間足", "4時間足", "日足", "週足", "月足"
])

# 時間足に応じてパラメータ
interval_map = {
    "1時間足": ("30d", "1h"),
    "4時間足": ("7d", "1h"),  # 再構成
    "日足":    ("6mo", "1d"),
    "週足":    ("1y", "1wk"),
    "月足":    ("5y", "1mo"),
}

if ticker_code and timeframe:
    period, interval = interval_map[timeframe]
    try:
        ticker = yf.Ticker(ticker_code)
        df = ticker.history(period=period, interval=interval)

        if timeframe == "4時間足":
            df = df.resample("4H").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            }).dropna()

        if df.empty:
            st.warning("データが取得できませんでした。銘柄コードや期間をご確認ください。")
        else:
            # 移動平均を計算
            df["13MA"] = df["Close"].rolling(window=13).mean()
            df["26MA"] = df["Close"].rolling(window=26).mean()

            # チャート描画
            fig = go.Figure()

            # ローソク足
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color='blue',
                decreasing_line_color='red',
                name="ローソク足"
            ))

            # 13日移動平均（黄）
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["13MA"],
                mode="lines",
                line=dict(color="yellow", width=1.5),
                name="13MA"
            ))

            # 26日移動平均（白）
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["26MA"],
                mode="lines",
                line=dict(color="white", width=1.5),
                name="26MA"
            ))

            fig.update_layout(
                title=f"{ticker_code} のチャート（{timeframe}）",
                xaxis_title="日付",
                yaxis_title="価格",
                plot_bgcolor="black",
                paper_bgcolor="black",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"エラーが発生しました：{e}")
