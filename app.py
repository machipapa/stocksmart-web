import streamlit as st
import pandas as pd

# 仮データ（後でAPI連携など可能）
data = {
    '銘柄コード': ['6758', '4385', '6594', '6920', '7203'],
    '銘柄名': ['ソニーグループ', 'メルカリ', '日本電産', 'レーザーテック', 'トヨタ自動車'],
    'PER': [12.3, 105.2, 11.2, 45.5, 9.1],
    '出来高増加率': [180, 130, 220, 110, 95],
    '業績成長率': [22, 15, 18, 8, 12],
    'MAクロス': [True, True, True, False, False],
    '上昇トレンド': [True, True, True, False, True],
}

def calculate_score(row):
    score = 0
    if row['MAクロス']:
        score += 1
    if 5 <= row['PER'] <= 15:
        score += 1
    if row['出来高増加率'] >= 150:
        score += 1
    if row['業績成長率'] >= 10:
        score += 1
    if row['上昇トレンド']:
        score += 1
    return score

# アプリタイトル
st.title('📈 StockSmart Web - 株スクリーニング')

# 検索入力欄
search_term = st.text_input("🔍 銘柄名またはコードで検索", "").strip()

# データフレーム作成＆スコア計算
df = pd.DataFrame(data)
df['スコア'] = df.apply(calculate_score, axis=1)
df = df.sort_values(by='スコア', ascending=False)

# 検索ワードでフィルタ
if search_term:
    df = df[df['銘柄名'].str.contains(search_term, case=False, na=False) |
            df['銘柄コード'].str.contains(search_term)]

# 結果表示
if df.empty:
    st.warning("一致する銘柄が見つかりませんでした。")
else:
    for i, row in df.iterrows():
        st.subheader(f"{row['銘柄名']}（{row['銘柄コード']}） - スコア：{row['スコア']} / 5")
        st.write(f"PER：{row['PER']}｜出来高増加：{row['出来高増加率']}%｜成長率：{row['業績成長率']}%") 
        st.write(f"MAクロス：{'◯' if row['MAクロス'] else '×'}｜上昇トレンド：{'◯' if row['上昇トレンド'] else '×'}")
        st.markdown('---')
