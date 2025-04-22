import streamlit as st import pandas as pd import json import os import unicodedata

st.set_page_config(page_title="🏇 出馬表フィルタ", layout="wide")

CSS: 印のselectboxを白背景・黒文字に。ドロップダウン候補にも強制適用。

st.markdown(""" <style> div[data-baseweb="select"] { background-color: white !important; color: black !important; border-radius: 5px; } div[data-baseweb="popover"] { background-color: white !important; color: black !important; } div[data-baseweb="menu"] { background-color: white !important; color: black !important; } ul[role="listbox"] { background-color: white !important; color: black !important; } div[role="option"] { background-color: white !important; color: black !important; } td { padding-top: 2px !important; padding-bottom: 2px !important; } </style> """, unsafe_allow_html=True)

st.title(":clipboard: 出馬表フィルタ - 印・馬柄横並び表示 + メモ")

印リスト = ["", "◎", "◎", "○", "▲", "△", "⭐️", "×", "消"]

MEMO_PATH = "local_memo.json"

if os.path.exists(MEMO_PATH): with open(MEMO_PATH, "r", encoding="utf-8") as f: memo_data = json.load(f) else: memo_data = {}

THEME = st.get_option("theme.base") TEXT_COLOR = "black" if THEME == "light" else "white"

def level_to_colored_star(lv): try: lv = str(lv).strip() lv = unicodedata.normalize('NFKC', lv).upper() star_map = { "A": ("★★★★★", "red"), "B": ("★★★★☆", "orange"), "C": ("★★★☆☆", "gray"), "D": ("★★☆☆☆", "blue"), "E": ("★☆☆☆☆", "teal") } stars, color = star_map.get(lv, ("☆☆☆☆☆", "lightgray")) return f"<span style='color:{color}; font-weight:bold'>{stars}</span>" except: return "<span style='color:gray'>☆☆☆☆☆</span>"

def format_past_row(row): try: positions = [] for col in ["2角", "3角", "4角"]: val = row.get(col) if pd.notnull(val): positions.append(str(int(float(val)))) pos_text = "→".join(positions) if positions else ""

agari = row.get("上り3F", "")
    chakujun = row.get("着順", "")
    kyori = row.get("距離", "")
    time = row.get("走破タイム", "")
    level = row.get("レース印３", "")
    weight = row.get("馬体重", "")
    kinryo = row.get("斤量", "")
    jokey = row.get("騎手", "")

    html = f"""
    <div style='line-height:1.1; font-size:11px; text-align:center; min-height:100px; color:{TEXT_COLOR};'>
        <div style='font-size:14px; font-weight:bold;'>{chakujun}</div>
        <div>{kyori}m / {time} / {level_to_colored_star(level)}</div>
        <div style='font-size:10px;'>
            {agari} / {pos_text}<br>
            {weight}kg / {kinryo} / {jokey}
        </div>
    </div>
    """
    return html
except Exception as e:
    return f"<div style='min-height:100px;'>Error: {e}</div>"

def display_race_table(df, race_label): for idx, row in df.iterrows(): col1, col2, col3 = st.columns([0.3, 2, 12]) with col1: mark = st.selectbox("", 印リスト, key=f"mark_{race_label}{row['馬名']}{idx}", label_visibility="collapsed") st.markdown(f"<div style='font-size:20px; text-align:center;'>{mark}</div>", unsafe_allow_html=True) with col2: st.markdown(f"<div style='text-align:center; font-weight:bold; color:{TEXT_COLOR};'>{row['馬名']}<br><span style='font-size:11px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span></div>", unsafe_allow_html=True) with st.expander("📝", expanded=False): memo = memo_data.get(row["馬名"], "") new_memo = st.text_area("", memo, key=f"memo_{race_label}{row['馬名']}{idx}") memo_data[row["馬名"]] = new_memo with col3: html_row = "<table style='width:100%; text-align:center'><tr>" for col in [f"{i}走前" for i in range(1, 6)]: html = row[col] if pd.notnull(row[col]) else f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>" html_row += f"<td style='vertical-align:top; min-width:150px'>{html}</td>" html_row += "</tr></table>" st.markdown(html_row, unsafe_allow_html=True)

if st.button("📂 メモをローカルjsonに保存", key=f"save_memo_{race_label}"):
    with open(MEMO_PATH, "w", encoding="utf-8") as f:
        json.dump(memo_data, f, ensure_ascii=False, indent=2)
    st.success("メモをlocal_memo.jsonに保存しました")

           {agari} / {pos_text}<br>
            {weight}kg / {kinryo} / {jokey}
        </div>
    </div>
    """
    return html
except Exception as e:
    return f"<div style='min-height:100px;'>Error: {e}</div>"

以下略（元のコードは維持）

