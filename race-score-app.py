import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="🏇 出馬表フィルタ", layout="wide")
st.title(":clipboard: 出馬表フィルタ - 印・馬柄横並び表示 + メモ")

印リスト = ["", "◎", "◎", "○", "▲", "△", "⭐️", "×", "消"]
MEMO_PATH = "local_memo.json"

if os.path.exists(MEMO_PATH):
    with open(MEMO_PATH, "r", encoding="utf-8") as f:
        memo_data = json.load(f)
else:
    memo_data = {}


def level_to_colored_star(lv):
    lv = str(lv).strip().upper()
    star_map = {
        "A": ("★★★★★", "red"),
        "B": ("★★★★☆", "orange"),
        "C": ("★★★☆☆", "gray"),
        "D": ("★★☆☆☆", "blue"),
        "E": ("★☆☆☆☆", "teal")
    }
    stars, color = star_map.get(lv, ("☆☆☆☆☆", "lightgray"))
    return f"<span style='color:{color}; font-weight:bold'>{stars}</span>"


def format_past_row(row):
    try:
        positions = []
        for col in ["2角", "3角", "4角"]:
            val = row.get(col)
            if pd.notnull(val):
                positions.append(str(int(float(val))))
        pos_text = "→".join(positions)

        agari = row["上り3F"]
        return f"""
        <div style='line-height:1.2; font-size:11px; text-align:center; min-height:120px;'>
            <div style='font-size:15px; font-weight:bold;'>{row['着順']}</div>
            <div>{row['距離']}m / {row['走破タイム']} / {level_to_colored_star(row['レース印３'])}</div>
            <div style='font-size:10px;'>
                {agari} / {pos_text}<br>
                {row['馬体重']}kg / {row['斤量']} / {row['騎手']}
            </div>
        </div>
        """
    except:
        return "<div style='min-height:120px;'></div>"


def generate_past5_display(df_shutsuba, entry_names):
    df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)].copy()
    df_filtered["日付"] = pd.to_datetime(df_filtered["日付(yyyy.mm.dd)"], errors="coerce")
    df_filtered = df_filtered.sort_values(["馬名", "日付"], ascending=[True, False])

    result = []
    for horse in df_filtered["馬名"].unique():
        df_horse = df_filtered[df_filtered["馬名"] == horse]
        rows = [format_past_row(row) for _, row in df_horse.head(5).iterrows()]
        while len(rows) < 5:
            rows.append("<div style='min-height:120px;'>ー</div>")
        result.append([horse] + rows)

    df_past5 = pd.DataFrame(result, columns=["馬名"] + [f"{i+1}走前" for i in range(5)])
    return df_past5


def display_race_table(df, race_label):
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([0.3, 2, 12])
        with col1:
            mark = st.selectbox("", 印リスト, key=f"mark_{race_label}_{row['馬名']}_{idx}", label_visibility="collapsed")
        with col2:
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>{row['馬名']}<br><span style='font-size:11px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span></div>", unsafe_allow_html=True)
        with col3:
            html_row = "<table style='width:100%; text-align:center'><tr>"
            for col in [f"{i}走前" for i in range(1, 6)]:
                html = row[col] if pd.notnull(row[col]) else "<div style='min-height:120px;'>ー</div>"
                html_row += f"<td style='vertical-align:top;'>{html}</td>"
            html_row += "</tr></table>"
            st.markdown(html_row, unsafe_allow_html=True)

        if st.toggle(f"📝", key=f"toggle_{race_label}_{row['馬名']}_{idx}"):
            memo = memo_data.get(row["馬名"], "")
