import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏇 出馬表（レースレベル付き）", layout="wide")
st.title("📋 出馬表フィルタ（G列レースレベル直読み）")

# CSVアップロード
entry_csv = st.file_uploader("📤 出走予定馬CSV（馬名・レース名）", type="csv")
shutsuba_csv = st.file_uploader("📤 出馬表CSV（G列にA〜Eのレースレベル）", type="csv")

if entry_csv and shutsuba_csv:
    df_entry = pd.read_csv(entry_csv, encoding="utf-8-sig")
    df_shutsuba = pd.read_csv(shutsuba_csv, encoding="shift_jis")

    # 列名クレンジング
    df_entry.columns = [col.strip() for col in df_entry.columns]
    df_shutsuba.columns = [col.strip() for col in df_shutsuba.columns]

    # 列の特定
    horse_col = df_shutsuba.columns[4]      # E列 = 馬名
    date_col = df_shutsuba.columns[1]       # B列 = 日付
    dist_col = df_shutsuba.columns[2]       # C列 = 距離
    time_col = "走破タイム"
    level_col = "レース印３"                # G列の列名

    # ★変換関数
    def level_to_star(lv):
        lv = str(lv).strip().replace("Ａ", "A").replace("Ｂ", "B").replace("Ｃ", "C").replace("Ｄ", "D").replace("Ｅ", "E")
        return {
            "A": "★★★★★",
            "B": "★★★★☆",
            "C": "★★★☆☆",
            "D": "★★☆☆☆",
            "E": "★☆☆☆☆",
        }.get(lv, "ー")

    if "馬名" in df_entry.columns:
        entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
        df_filtered = df_shutsuba[df_shutsuba[horse_col].astype(str).str.strip().isin(entry_names)].copy()

        df_filtered[date_col] = pd.to_datetime(df_filtered[date_col], errors="coerce")
        df_filtered["★"] = df_filtered[level_col].map(level_to_star)

        # 過去走まとめ列
        df_filtered["まとめ"] = (
            df_filtered[date_col].dt.strftime("%m/%d") + " "
            + df_filtered[dist_col].astype(str) + "m "
            + df_filtered[time_col].astype(str) + " "
            + df_filtered["★"]
        )

        # 馬名ごとに5走分を横並びに整理
        df_filtered = df_filtered.sort_values([horse_col, date_col], ascending=[True, False])
        grouped = df_filtered.groupby(horse_col)["まとめ"].apply(lambda x: x.tolist()[:5]).reset_index()
        df_past5 = grouped.set_index(horse_col)["まとめ"].apply(pd.Series)
        df_past5.columns = [f"{i+1}走前" for i in range(df_past5.shape[1])]
        df_past5.reset_index(inplace=True)
        df_past5.rename(columns={horse_col: "馬名"}, inplace=True)

        # 出走予定馬とマージ
        df_show = pd.merge(df_entry, df_past5, on="馬名", how="left")

        # レース名でグループ分け表示
        race_names = df_show["レース名"].dropna().unique().tolist()
        tabs = st.tabs(race_names)

        for i, race in enumerate(race_names):
            with tabs[i]:
                race_df = df_show[df_show["レース名"] == race].drop(columns=["レース名"]).reset_index(drop=True)
                st.markdown(f"### 📄 {race}")
                st.dataframe(race_df)

                csv = race_df.to_csv(index=False, encoding="utf-8-sig")
                st.download_button("📥 CSVダウンロード", csv, file_name=f"{race}_出馬表.csv", key=race)

    else:
        st.error("❌ 出走予定馬CSVに '馬名' 列が見つかりませんでした。")

else:
    st.info("🔽 出走予定馬CSVと出馬表CSVの2つをアップロードしてください。")
