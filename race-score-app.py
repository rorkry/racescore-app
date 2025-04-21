import streamlit as st import pandas as pd import json import os import unicodedata

st.set_page_config(page_title="🏇 出馬表フィルタ", layout="wide")

CSSスタイル調整

st.markdown(""" <style> div[data-baseweb="select"] { background-color: white !important; color: black !important; border-radius: 5px; } div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], div[role="option"] { background-color: white !important; color: black !important; } .memo-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.4); display: flex; justify-content: center; align-items: center; z-index: 9999; } .memo-box { background: white; color: black; padding: 20px; border-radius: 10px; width: 400px; box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.3); } </style> """, unsafe_allow_html=True)

st.title(":clipboard: 出馬表フィルタ - 印・馬柄横並び表示 + メモ")

印リスト = ["", "◎", "◎", "○", "▲", "△", "⭐️", "×", "消"]

MEMO_PATH = "local_memo.json" if os.path.exists(MEMO_PATH): with open(MEMO_PATH, "r", encoding="utf-8") as f: memo_data = json.load(f) else: memo_data = {}

THEME = st.get_option("theme.base") TEXT_COLOR = "black" if THEME == "light" else "white"

selected_memo_horse = st.session_state.get("selected_memo_horse", "")

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
    <div style='line-height:1.2; font-size:11px; text-align:center; min-height:120px; color:{TEXT_COLOR};'>
        <div style='font-size:15px; font-weight:bold;'>{chakujun}</div>
        <div>{kyori}m / {time} / {level_to_colored_star(level)}</div>
        <div style='font-size:10px;'>
            {agari} / {pos_text}<br>
            {weight}kg / {kinryo} / {jokey}
        </div>
    </div>
    """
    return html
except Exception as e:
    return f"<div style='min-height:120px;'>Error: {e}</div>"

def generate_past5_display(df_shutsuba, entry_names): df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)].copy() if "日付(yyyy.mm.dd)" in df_filtered.columns: df_filtered["日付"] = pd.to_datetime(df_filtered["日付(yyyy.mm.dd)"], errors="coerce") df_filtered = df_filtered.sort_values(["馬名", "日付"], ascending=[True, False])

result = []
for horse in df_filtered["馬名"].unique():
    df_horse = df_filtered[df_filtered["馬名"] == horse]
    rows = [format_past_row(row) for _, row in df_horse.head(5).iterrows()]
    while len(rows) < 5:
        rows.append(f"<div style='min-height:120px; color:{TEXT_COLOR};'>ー</div>")
    result.append([horse] + rows)

df_past5 = pd.DataFrame(result, columns=["馬名"] + [f"{i+1}走前" for i in range(5)])
return df_past5

def display_race_table(df, race_label): global selected_memo_horse for idx, row in df.iterrows(): col1, col2, col3 = st.columns([0.3, 2, 12]) with col1: mark = st.selectbox("", 印リスト, key=f"mark_{race_label}{row['馬名']}{idx}", label_visibility="collapsed") st.markdown(f"<div style='font-size:20px; text-align:center;'>{mark}</div>", unsafe_allow_html=True) with col2: st.markdown(f"<div style='text-align:center; font-weight:bold; color:{TEXT_COLOR};'>{row['馬名']}<br><span style='font-size:11px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span></div>", unsafe_allow_html=True) if st.button("📝", key=f"memo_btn_{race_label}{row['馬名']}{idx}"): st.session_state["selected_memo_horse"] = row["馬名"] with col3: html_row = "<table style='width:100%; text-align:center'><tr>" for col in [f"{i}走前" for i in range(1, 6)]: html = row[col] if pd.notnull(row[col]) else f"<div style='min-height:120px; color:{TEXT_COLOR};'>ー</div>" html_row += f"<td style='vertical-align:top; min-width:150px'>{html}</td>" html_row += "</tr></table>" st.markdown(html_row, unsafe_allow_html=True)

if selected_memo_horse:
    st.markdown("<div class='memo-overlay'>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='memo-box'>", unsafe_allow_html=True)
        st.markdown(f"### 📝 {selected_memo_horse} へのメモ")
        memo = memo_data.get(selected_memo_horse, "")
        new_memo = st.text_area("", memo, key=f"popup_memo_{selected_memo_horse}")
        if st.button("💾 保存"):
            memo_data[selected_memo_horse] = new_memo
            with open(MEMO_PATH, "w", encoding="utf-8") as f:
                json.dump(memo_data, f, ensure_ascii=False, indent=2)
            st.session_state["selected_memo_horse"] = ""
        if st.button("❌ 閉じる"):
            st.session_state["selected_memo_horse"] = ""
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

entry_file = st.file_uploader("出走予定馬CSV", type="csv") shutsuba_file = st.file_uploader("出馬表CSV", type="csv")

if entry_file and shutsuba_file: df_entry = pd.read_csv(entry_file, encoding="utf-8") df_shutsuba = pd.read_csv(shutsuba_file, encoding="shift_jis")

df_entry.columns = [c.strip() for c in df_entry.columns]
df_shutsuba.columns = [c.strip() for c in df_shutsuba.columns]

df_entry.drop(columns=["クラス名", "馬場状態", "距離", "頭数", "所在地"], errors="ignore", inplace=True)
df_entry["調教師"] = df_entry["所属"].astype(str) + "/" + df_entry["調教師"].astype(str)
df_entry.drop(columns=["所属"], inplace=True)

entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
df_past5 = generate_past5_display(df_shutsuba, entry_names)
df_merged = pd.merge(df_entry, df_past5, on="馬名", how="left")

df_merged["表示レース名"] = df_merged["開催地"].astype(str) + df_merged["R"].astype(str) + "R " + df_merged["レース名"].astype(str)

for race_name in df_merged["表示レース名"].unique():
    with st.expander(f"🏁 {race_name}"):
        race_df = df_merged[df_merged["表示レース名"] == race_name].reset_index(drop=True)
        display_race_table(race_df, race_name)


