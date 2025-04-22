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
    lv = str(lv).strip()
    lv = unicodedata.normalize('NFKC', lv).upper()
    star_map = {
        "A": ("★★★★★", "red"),
        "B": ("★★★★☆", "orange"),
        "C": ("★★★☆☆", "white"),
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
    kyori = row.get("距離", "")
    time = row.get("走破タイム", "")
    level = row.get("レース印３", "")
    weight = row.get("馬体重", "")
    kinryo = row.get("斤量", "")
    jokey = row.get("騎手", "")
    date = row.get("日付", "")

    html = f"""
    <div style='line-height:1.1; font-size:10px; text-align:center; color:{TEXT_COLOR}; min-height:100px'>
        <div style='font-size:13px; font-weight:bold;'>{chakujun}</div>
        <div>{date} / {kyori}m / {time} / {level_to_colored_star(level)}</div>
        <div>{agari} / {pos_text}<br>{weight}kg / {kinryo} / {jokey}</div>
    </div>
    """
    return html

def display_race_table(df, race_label):
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

# アップロード部
entry_file = st.file_uploader("出走予定馬CSV", type="csv")
shutsuba_file = st.file_uploader("出馬表CSV", type="csv")

if entry_file and shutsuba_file:
    df_entry = pd.read_csv(entry_file, encoding="utf-8")
    df_shutsuba = pd.read_csv(shutsuba_file, encoding="shift_jis")

    df_entry.columns = [c.strip() for c in df_entry.columns]
    df_shutsuba.columns = [c.strip() for c in df_shutsuba.columns]

    df_entry.drop(columns=["クラス名", "馬場状態", "距離", "頭数", "所在地"], errors="ignore", inplace=True)
    df_entry["調教師"] = df_entry["所属"].astype(str) + "/" + df_entry["調教師"].astype(str)
    df_entry.drop(columns=["所属"], inplace=True)

    # 日付変換
    if "日付(yyyy.mm.dd)" in df_shutsuba.columns:
        df_shutsuba["日付"] = pd.to_datetime(df_shutsuba["日付(yyyy.mm.dd)"].astype(str).str.replace("\\.", "-"), errors="coerce")
        df_shutsuba = df_shutsuba.sort_values(["馬名", "日付"], ascending=[True, False])

    entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
    df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)].copy()

    result = []
    for horse in df_filtered["馬名"].unique():
        df_horse = df_filtered[df_filtered["馬名"] == horse]
        rows = [format_past_row(row) for _, row in df_horse.head(5).iterrows()]
        while len(rows) < 5:
            rows.append(f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>")
        result.append([horse] + rows)

    df_past5 = pd.DataFrame(result, columns=["馬名"] + [f"{i+1}走前" for i in range(5)])
    df_merged = pd.merge(df_entry, df_past5, on="馬名", how="left")

    # 開催日・開催地によるタブ切替
    df_merged["開催日"] = df_merged["日付コード"].astype(str).apply(lambda x: f"{int(x[:1])}月{int(x[1:])}日") if "日付コード" in df_merged.columns else "不明"
    selected_date = st.selectbox("📅 開催日を選択", sorted(df_merged["開催日"].dropna().unique()))
    df_date = df_merged[df_merged["開催日"] == selected_date]

    place_tabs = st.tabs(sorted(df_date["開催地"].dropna().unique()))
    for i, place in enumerate(sorted(df_date["開催地"].dropna().unique())):
        with place_tabs[i]:
            df_place = df_date[df_date["開催地"] == place]
            df_place["表示レース名"] = df_place["R"].astype(str) + "R " + df_place["レース名"].astype(str)
            for race_name in df_place["表示レース名"].unique():
                with st.expander(f"🏁 {race_name}"):
                    race_df = df_place[df_place["表示レース名"] == race_name].reset_index(drop=True)
                    display_race_table(race_df, race_name)
