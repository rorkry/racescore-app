import streamlit as st
import pandas as pd

st.set_page_config(page_title="出馬表（レース別タブ切替）", layout="wide")
st.title("🏇 出走予定馬の過去5走（★付き）")

# ファイルアップロード
entry_csv = st.file_uploader("📤 整形済_出走予定馬.csv", type="csv")
past_csv = st.file_uploader("📤 過去5走（★付き）CSV", type="csv")

if entry_csv and past_csv:
    df_entry = pd.read_csv(entry_csv, encoding="utf-8-sig")
    df_past = pd.read_csv(past_csv, encoding="utf-8-sig")

    # クレンジング
    df_entry["馬名"] = df_entry["馬名"].astype(str).str.strip()
    df_entry["レース名"] = df_entry["レース名"].astype(str).str.strip()

    # 出馬表生成
    df_combined = pd.merge(df_entry[["レース名", "馬名"]], df_past, on="馬名", how="left")
    race_groups = df_combined.groupby("レース名")
    race_names = list(race_groups.groups.keys())

    # 🔁 タブ表示
    tabs = st.tabs(race_names)
    for i, race in enumerate(race_names):
        with tabs[i]:
            race_df = race_groups.get_group(race).drop(columns=["レース名"]).reset_index(drop=True)
            st.markdown(f"### 📋 {race}")
            st.dataframe(race_df)

            # ダウンロード
            csv = race_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 CSVをダウンロード", csv, file_name=f"{race}_出馬表.csv", key=race)
else:
    st.info("🔽 上記2つのCSVファイルをアップロードしてください。")
