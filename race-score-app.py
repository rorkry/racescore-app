import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from io import StringIO

st.set_page_config(page_title="レース出馬表スコア表示", layout="wide")
st.title("🏇 出馬表（レースレベルA/Bスコア付き）")

# ファイルアップロード
def upload_csv(label):
    uploaded_file = st.file_uploader(label, type=["csv"])
    if uploaded_file:
        try:
            return pd.read_csv(uploaded_file, encoding="shift_jis")
        except:
            return pd.read_csv(uploaded_file)
    return None

entry_df = upload_csv("🔼 出馬表CSVをアップロード")
level_df = upload_csv("🔼 レースレベルマスタCSVをアップロード")

if entry_df is not None and level_df is not None:
    # RX除去
    entry_df["race_id_cleaned"] = entry_df["レースID(新/馬番無)"].astype(str).str.replace("RX", "")

    # レベルマスタ整形
    level_df.columns = ["date", "race_id", "rating_raw"]
    level_df["race_id_cleaned"] = level_df["race_id"].astype(str)
    zenkaku_to_hankaku = str.maketrans("ＡＢＣＤＥ", "ABCDE")
    def extract_last_zenkaku_letter(text):
        matches = re.findall(r'[Ａ-Ｅ]', str(text))
        if matches:
            return matches[-1].translate(zenkaku_to_hankaku)
        return None
    level_df["rating_letter"] = level_df["rating_raw"].apply(extract_last_zenkaku_letter)
    score_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}
    level_df["race_score_A"] = level_df["rating_letter"].map(score_map)

    # 特徴量選定
    cols_to_use = ["race_id_cleaned", "距離", "走破タイム", "基準タイム", "馬場状態", "上がり3F", "RPCI", "年齢", "馬体重", "斤量", "騎手", "調教師", "頭数", "人気"]
    df_features = entry_df[[col for col in cols_to_use if col in entry_df.columns]].copy()
    df_grouped = df_features.groupby("race_id_cleaned").agg("first").reset_index()

    # A方式スコア結合
    df = pd.merge(df_grouped, level_df[["race_id_cleaned", "race_score_A"]], on="race_id_cleaned", how="left")

    # ★表示
    def score_to_stars(score):
        if pd.isna(score): return ""
        score = int(score)
        return "★" * score + "☆" * (5 - score)

    df["Aスコア"] = df["race_score_A"].apply(score_to_stars)

    # Bスコアゲージ表示
    def render_gauge(score):
        if pd.isna(score): return ""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            gauge = {
                'axis': {'range': [0, 5]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range': [0, 2], 'color': "#eee"},
                    {'range': [2, 4], 'color': "#ccd"},
                    {'range': [4, 5], 'color': "#bbf"},
                ]
            },
            number={'suffix': ""},
        ))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10))
        return fig

    # Bスコア予測（仮にランダムで生成中。モデル連携で置き換え可）
    import numpy as np
    df["race_score_B"] = np.random.uniform(1, 5, len(df)).round(1)

    st.markdown("### 出馬表（レースレベル）")
    for _, row in df.iterrows():
        cols = st.columns([3, 1, 2])
        cols[0].markdown(f"**距離:** {row['距離']} ／ **馬場:** {row['馬場状態']} ／ **基準タイム:** {row['基準タイム']}")
        cols[1].markdown(f"A方式：{row['Aスコア']}")
        with cols[2]:
            st.plotly_chart(render_gauge(row['race_score_B']), use_container_width=True)

else:
    st.info("CSVを2つアップロードしてください（出馬表 / レースレベルマスタ）")
