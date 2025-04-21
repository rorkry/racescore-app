import streamlit as st
import pandas as pd

st.set_page_config(page_title="出馬表（レース別切替）", layout="wide")
st.title("📋 出走予定馬の過去5走（★付き） - レースごとに表示")

# アップロード欄
entry_csv = st.file_uploader("🔽 整形済_出走予定馬.csv", type="csv")
past_csv = st.file_uploader("🔽 過去5走（★付き）CSV", type="csv")

if entry_csv and past_csv:
    df_entry = pd.read_csv(entry_csv, encoding="utf-8-sig")
    df_past = pd.read_csv(past_csv, encoding="utf-8-sig")

    # 前処理
    df_entry["馬名"] = df_entry["馬名"].astype(str).str.strip()
    df_entry["レース名"] = df_entry["レース名"].astype(str).str.strip()

    # レースごとに結合
    df_combined = pd.merge(df_entry[["レース名", "馬名"]], df_past, on="馬名", how="left")
    race_groups = df_combined.groupby("レース名")

    race_names = list(race_groups.groups.keys())
    selected_race = st.selectbox("🎯 レースを選択してください", race_names)

    # 選択されたレースの出馬表を表示
    race_df = race_groups.get_group(selected_race).drop(columns=["レース名"]).reset_index(drop=True)
    st.markdown(f"### 📄 {selected_race}")
    st.dataframe(race_df)

    # ダウンロードボタン（任意）
    csv = race_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 この出馬表をCSVでダウンロード", csv, file_name=f"{selected_race}_出馬表.csv")
else:
    st.info("📤 上記2つのCSVファイルをアップロードしてください。")
