import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="横並び出馬表（過去5走付き）", layout="wide")
st.title("🏇 横並び出馬表（過去5走＋スコア）")

# CSVファイルのアップロード（手動）
entry_file = st.file_uploader("🔼 出馬表CSVをアップロード", type="csv")
level_file = st.file_uploader("🔼 レースレベルマスタCSVをアップロード", type="csv")

if entry_file and level_file:
    entry_df = pd.read_csv(entry_file, encoding="shift_jis")
    level_df = pd.read_csv(level_file, encoding="shift_jis", header=None)
    level_df.columns = ["date", "race_id", "rating_raw"]

    # RX除去と整形
    entry_df["race_id"] = entry_df["レースID(新/馬番無)"].astype(str).str.replace("RX", "")
    level_df["race_id"] = level_df["race_id"].astype(str)

    zenkaku_to_hankaku = str.maketrans("ＡＢＣＤＥ", "ABCDE")
    def extract_level(text):
        matches = re.findall(r"[Ａ-Ｅ]", str(text))
        if matches:
            return matches[-1].translate(zenkaku_to_hankaku)
        return None

    level_df["level"] = level_df["rating_raw"].apply(extract_level)
    score_map = {'A': '★★★★★', 'B': '★★★★☆', 'C': '★★★☆☆', 'D': '★★☆☆☆', 'E': '★☆☆☆☆'}
    level_df["level_star"] = level_df["level"].map(score_map)

    # 結合
    merged = pd.merge(entry_df, level_df[["race_id", "level_star"]], on="race_id", how="left")
    merged = merged.sort_values(by=["馬名", "race_id"], ascending=[True, True])

    # 各馬の過去5走をまとめる
    def format_row(row):
        return f"{row['日付(yyyy.mm.dd)']}\n{row['距離']} {row['馬場状態']}\n{row['走破タイム']} {row['level_star']}"

    if not merged.empty:
        if "まとめ" not in merged.columns:
            merged["まとめ"] = merged.apply(format_row, axis=1)

        # 高速化：辞書でグループ化
        horse_groups = dict(tuple(merged.groupby("馬名")))
        rows = []

        for name, runs in horse_groups.items():
            summary = runs.sort_values("race_id")["まとめ"].tail(5).tolist()
            row = [name] + summary + ["" for _ in range(5 - len(summary))]
            rows.append(row)

        columns = ["馬名"] + [f"{i+1}走前" for i in range(5)]
        final = pd.DataFrame(rows, columns=columns)

        if not final.empty:
            # 検索UI
            selected_horse = st.selectbox("🐴 馬名で検索", final["馬名"].unique())
            filtered = final[final["馬名"] == selected_horse]
            st.dataframe(filtered, use_container_width=True)
        else:
            st.warning("出走馬に5走以上のデータがありません。")
    else:
        st.warning("アップロードされた出馬表データが空、または整形に失敗しました。")

else:
    st.info("出馬表CSVとレースレベルマスタCSVをアップロードしてください。")
