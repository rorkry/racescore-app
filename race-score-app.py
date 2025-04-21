import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏇 出馬表（最小構成）", layout="wide")
st.title("📋 出馬表（レースレベル★付き・レース別表示）")

# ファイルアップロード
entry_csv = st.file_uploader("📤 出走予定馬.csv（馬名＋レース名）", type="csv")
shutsuba_csv = st.file_uploader("📤 出馬表.csv（過去走込み、G列にレースレベル）", type="csv")

if entry_csv and shutsuba_csv:
    df_entry = pd.read_csv(entry_csv, encoding="utf-8-sig")
    df_shutsuba = pd.read_csv(shutsuba_csv, encoding="shift_jis")

    # 列名整備
    df_entry.columns = [col.strip() for col in df_entry.columns]
    df_shutsuba.columns = [col.strip() for col in df_shutsuba.columns]

    # 馬名列推定（出馬表は E列、レベルは G列と想定）
    entry_horse_col = "馬名"
    shutsuba_horse_col = df_shutsuba.columns[4]  # E列
    level_col = df_shutsuba.columns[6]  # G列

    # ★変換関数
    def level_to_star(lv):
        return {
            "A": "★★★★★",
            "B": "★★★★☆",
            "C": "★★★☆☆",
            "D": "★★☆☆☆",
            "E": "★☆☆☆☆",
        }.get(str(lv).strip(), "ー")

    if entry_horse_col in df_entry.columns:
        entry_names = df_entry[entry_horse_col].astype(str).str.strip().unique().tolist()
        df_filtered = df_shutsuba[df_shutsuba[shutsuba_horse_col].astype(str).str.strip().isin(entry_names)].copy()

        # 日付整形
        if "日付" in df_filtered.columns:
            df_filtered["日付"] = pd.to_datetime(df_filtered["日付"], errors="coerce")

        # ★列追加
        df_filtered["★"] = df_filtered[level_col].map(level_to_star)

        # 過去5走まとめ列作成
        df_filtered["まとめ"] = (
            df_filtered["日付"].dt.strftime("%m/%d") + " "
            + df_filtered["距離"].astype(str) + "m "
            + df_filtered["走破タイム"].astype(str) + " "
            + df_filtered["★"]
        )

        df_filtered = df_filtered.sort_values(["馬名", "日付"], ascending=[True, False])
        grouped = df_filtered.groupby(shutsuba_horse_col)["まとめ"].apply(lambda x: x.tolist()[:5]).reset_index()
        df_past5 = grouped.set_index(shutsuba_horse_col)["まとめ"].apply(pd.Series)
        df_past5.columns = [f"{i+1}走前" for i in range(df_past5.shape[1])]
        df_past5.reset_index(inplace=True)
        df_past5.rename(columns={shutsuba_horse_col: "馬名"}, inplace=True)

        # 出走予定馬と結合（レース名を加える）
        df_show = pd.merge(df_entry, df_past5, on="馬名", how="left")

        # レースごとに表示
        race_names = df_show["レース名"].unique().tolist()
        tabs = st.tabs(race_names)

        for i, race in enumerate(race_names):
            with tabs[i]:
                race_df = df_show[df_show["レース名"] == race].drop(columns=["レース名"]).reset_index(drop=True)
                st.markdown(f"### 📄 {race}")
                st.dataframe(race_df)

                csv = race_df.to_csv(index=False, encoding="utf-8-sig")
                st.download_button("📥 この出馬表をCSVダウンロード", csv, file_name=f"{race}_出馬表.csv", key=race)
    else:
        st.error("❌ 出走予定馬CSVに '馬名' 列が見つかりませんでした。")

else:
    st.info("🔽 上記2つのCSVファイルをアップロードしてください。")
