import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="🏇 出馬表フィルタ", layout="wide")

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

st.title(":clipboard: 出馬表フィルタ - 日付・開催地別タブ表示")

TEXT_COLOR = "black" if st.get_option("theme.base") == "light" else "white"


def convert_numeric_date(code):
    code_str = str(int(code)).zfill(3)
    month = int(code_str[:-2])
    day = int(code_str[-2:])
    return f"{month}月{day}日"


def level_to_colored_star(lv):
    lv = str(lv).strip()
    lv = unicodedata.normalize('NFKC', lv).upper()
    star_map = {
        "A": ("★★★★★", "red"),
        "B": ("★★★★☆", "orange"),
        "C": ("★★★☆☆", "violet"),
        "D": ("★★☆☆☆", "blue"),
        "E": ("★☆☆☆☆", "gray")
    }
    stars, color = star_map.get(lv, ("☆☆☆☆☆", "lightgray"))
    return f"<span style='color:{color}; font-weight:bold'>{stars}</span>"


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
        <div>{date} / {kyori}m / {time} / {level_to_colored_star(level)}</div>
        <div>{agari} / {pos_text}<br>{weight}kg / {kinryo} / {jokey}</div>
    </div>
    """
    return html


def display_race_table(df):
    for idx, row in df.iterrows():
        col1, col2 = st.columns([2, 12])
        with col1:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:{TEXT_COLOR};'>{row['馬名']}<br><span style='font-size:10px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span></div>",
                unsafe_allow_html=True
            )
        with col2:
            html_row = "<table style='width:100%; text-align:center; border-spacing:0'><tr>"
            for col in [f"{i}走前" for i in range(1, 6)]:
                html = row[col] if pd.notnull(row[col]) else f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>"
                html_row += f"<td style='vertical-align:top; min-width:140px'>{html}</td>"
            html_row += "</tr></table>"
            st.markdown(html_row, unsafe_allow_html=True)

# --- ファイルアップロード ---
entry_file = st.file_uploader("出走予定馬CSV", type="csv")
shutsuba_file = st.file_uploader("出馬表CSV", type="csv")

if entry_file and shutsuba_file:
    df_entry = pd.read_csv(entry_file, encoding="utf-8")
    df_shutsuba = pd.read_csv(shutsuba_file, encoding="shift_jis")

    df_entry.columns = [c.strip() for c in df_entry.columns]
    df_shutsuba.columns = [c.strip() for c in df_shutsuba.columns]

    df_entry["調教師"] = df_entry["所属"].astype(str) + "/" + df_entry["調教師"].astype(str)
    df_entry.drop(columns=["クラス名", "馬場状態", "距離", "頭数", "所在地", "所属"], errors="ignore", inplace=True)

    entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
    df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)].copy()

    df_filtered["日付"] = pd.to_datetime(df_filtered["日付(yyyy.mm.dd)"].astype(str).str.replace(" ", "").str.replace(".", "/", regex=False), errors="coerce")

    df_filtered = df_filtered.sort_values(["馬名", "日付"], ascending=[True, False])

    result = []
    for horse in df_filtered["馬名"].unique():
        df_horse = df_filtered[df_filtered["馬名"] == horse]
        rows = [format_past_row(row) for _, row in df_horse.head(5).iterrows()]
        while len(rows) < 5:
            rows.append(f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>")
        result.append([horse] + rows)

    df_past5 = pd.DataFrame(result, columns=["馬名"] + [f"{i+1}走前" for i in range(5)])
    df_merged = pd.merge(df_entry, df_past5, on="馬名", how="left")

    df_merged["開催日"] = df_merged["日付コード"].apply(convert_numeric_date)

    for date in sorted(df_merged["開催日"].unique()):
        with st.expander(f"📅 {date}"):
            df_date = df_merged[df_merged["開催日"] == date]
            locations = df_date["開催地"].unique()
            loc_tabs = st.tabs(locations)
            for i, loc in enumerate(locations):
                with loc_tabs[i]:
                    df_loc = df_date[df_date["開催地"] == loc]
                    for race_name in df_loc["R"].astype(str) + "R " + df_loc["レース名"]:
                        df_race = df_loc[df_loc["R"].astype(str) + "R " + df_loc["レース名"] == race_name]
                        st.markdown(f"### 🏁 {loc}{race_name}")
                        display_race_table(df_race.reset_index(drop=True))
