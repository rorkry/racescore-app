import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="🏇 出馬表フィルタ", layout="wide")

# スタイル（格子状＆コンパクトに）
st.markdown("""
    <style>
    td {
        padding-top: 1px !important;
        padding-bottom: 1px !important;
        border: 1px solid #ccc;
    }
    table {
        border-collapse: collapse;
    }
    </style>
""", unsafe_allow_html=True)

st.title(":clipboard: 出馬表フィルタ - シンプル表示")

TEXT_COLOR = "black" if st.get_option("theme.base") == "light" else "white"

def level_to_colored_star(lv):
    try:
        lv = str(lv).strip()
        lv = unicodedata.normalize('NFKC', lv).upper()
        star_map = {
            "A": ("★★★★★", "#FF5555"),
            "B": ("★★★★☆", "#FFA500"),
            "C": ("★★★☆☆", "#DDDD55"),
            "D": ("★★☆☆☆", "#88CCFF"),
            "E": ("★☆☆☆☆", "#BBBBBB")
        }
        stars, color = star_map.get(lv, ("☆☆☆☆☆", "#888888"))
        return f"<span style='color:{color}; font-weight:bold'>{stars}</span>"
    except:
        return "<span style='color:#888888'>☆☆☆☆☆</span>"

def format_past_row(row):
    positions = []
    for col in ["2角", "3角", "4角"]:
        val = row.get(col)
        if pd.notnull(val):
            positions.append(str(int(float(val))))
    pos_text = "→".join(positions) if positions else ""
    agari = row.get("上り3F", "")
    chakujun = row.get("着順", "")
    date = row.get("日付", "")
    kyori = row.get("距離", "")
    time = row.get("走破タイム", "")
    level = row.get("レース印３", "")
    weight = row.get("馬体重", "")
    kinryo = row.get("斤量", "")
    jokey = row.get("騎手", "")

    html = f"""
    <div style='line-height:1.1; font-size:10px; text-align:center; color:{TEXT_COLOR}; min-height:100px'>
        <div style='font-size:13px; font-weight:bold;'>{chakujun}</div>
        <div style='font-size:9px'>{date}</div>
        <div>{kyori}m / {time} / {level_to_colored_star(level)}</div>
        <div>{agari} / {pos_text}<br>{weight}kg / {kinryo} / {jokey}</div>
    </div>
    """
    return html

def display_race_table(df, race_label):
    for idx, row in df.iterrows():
        col1, col2 = st.columns([2, 12])

        with col1:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:{TEXT_COLOR}; border: 1px solid #ccc;'>"
                f"{row['馬名']}<br><span style='font-size:10px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col2:
            html_row = "<table style='width:100%; text-align:center; border-spacing:0'><tr>"
            for col in [f"{i}走前" for i in range(1, 6)]:
                html = row[col] if pd.notnull(row[col]) else f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>"
                html_row += f"<td style='vertical-align:top; min-width:140px'>{html}</td>"
            html_row += "</tr></table>"
            st.markdown(html_row, unsafe_allow_html=True)
