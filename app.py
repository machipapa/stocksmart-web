import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# スマホ幅対応CSS
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

# yfinance用 period / interval 対応表
interval_map = {
    "1時間足": ("30d", "1h"),
    "4時間足": ("7d", "1h"),
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
            # 移動平均計算
            df["13MA"] = df["Close"].rolling(window=13).mean()
            df["26MA"] = df["Close"].rolling(window=26).mean()

            # ▼▼▼ トレンド判定 ▼▼▼
            ma13 = df["13MA"].dropna()
            ma26 = df["26MA"].dropna()
            if len(ma13) >= 3 and len(ma26) >= 3:
                slope_13 = ma13.iloc[-1] - ma13.iloc[-3]
                slope_26 = ma26.iloc[-1] - ma26.iloc[-3]
                if ma13.iloc[-1] > ma26.iloc[-1] and slope_13 > 0 and slope_26 > 0:
                    trend = "🔵 上昇トレンド"
                elif ma13.iloc[-1] < ma26.iloc[-1] and slope_13 < 0 and slope_26 < 0:
                    trend = "🔴 下降トレンド"
                else:
                    trend = "⚪ 横ばい・レンジ"
            else:
                trend = "（トレンド判定不可）"

            st.markdown(f"### 📊 トレンド判定結果：**{trend}**")

            # ▼▼▼ チャート描画 ▼▼▼
            fig = go.Figure()

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

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["13MA"],
                mode="lines",
                line=dict(color="yellow", width=1.5),
                name="13MA"
            ))

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
                yaxis_title="",
                plot_bgcolor="black",
                paper_bgcolor="black",
                font_color="white",
                xaxis_rangeslider_visible=True,
                height=600,
                yaxis=dict(showticklabels=False),  # 👈 価格ラベルを非表示にする
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12)
                )
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"エラーが発生しました：{e}")
