import streamlit as st
import yfinance as yf

st.title("📈 StockSmart LIVE - 株価リアルタイム検索")

code = st.text_input("🔍 銘柄コードを入力してください（例：6758）", "6758")

if st.button("▶ 株価を取得する"):
    try:
        ticker = yf.Ticker(f"{code}.T")
        info = ticker.info
        hist = ticker.history(period="5d")

        st.subheader(f"{info.get('longName', '企業名取得エラー')}（{code}.T）")
        st.write(f"📊 PER：{info.get('trailingPE')}")
        st.write(f"💰 時価総額：{info.get('marketCap'):,} 円")

        st.line_chart(hist["Close"])

    except Exception as e:
        st.error(f"データ取得に失敗しました：{e}")
