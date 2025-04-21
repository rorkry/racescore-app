import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏇 出馬表フィルタ（強化表示）", layout="wide")
st.title("📋 出馬表フィルタ - 出走段階切替 + 過去走2段表示")

tab1, tab2 = st.tabs(["🟩 出走予定馬（想定）", "🟦 枠順確定後（確定出馬）"])

def level_to_colored_star(lv):
    lv = str(lv).strip().replace("Ａ", "A").replace("Ｂ", "B").replace("Ｃ", "C").replace("Ｄ", "D").replace("Ｅ", "E")
    stars = {
        "A": "★★★★★",
        "B": "★★★★☆",
        "C": "★★★☆☆",
        "D": "★★☆☆☆",
        "E": "★☆☆☆☆",
    }.get(lv, "ー")
    color_map = {
        "A": "red",
        "B": "orange",
        "C": "gray",
        "D": "blue",
        "E": "lightblue",
    }
    color = color_map.get(lv, "black")
    return f"<span style='color:{color}; font-weight:bold'>{stars}</span>"

def format_past_row(row):
    try:
        return f"""
        <div style='line-height:1.2; font-size:11px;'>
            <div style='font-size:15px; font-weight:bold;'>{row['着順']}</div>
            <div>{row['距離']}m / {row['走破タイム']} / {level_to_colored_star(row['レース印３'])}</div>
            <div style='font-size:10px;'>
                上り:{row['上り3F']} / 通過:{row['2角']}→{row['3角']}→{row['4角']}<br>
                馬体:{row['馬体重']}kg / 斤量:{row['斤量']} / 騎手:{row['騎手']}
            </div>
        </div>
        """
    except:
        return "ー"
        def generate_past5_display(df_shutsuba, entry_names):
    # 対象馬だけ抽出
    df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)].copy()
    df_filtered["日付"] = pd.to_datetime(df_filtered["日付(yyyy.mm.dd)"], errors="coerce")
    df_filtered = df_filtered.sort_values(["馬名", "日付"], ascending=[True, False])

    # 表示列加工
    past_cols = ["馬名", "日付", "距離", "走破タイム", "レース印３", "着順",
                 "上り3F", "2角", "3角", "4角", "馬体重", "斤量", "騎手"]
    df_filtered = df_filtered[past_cols].copy()
    df_filtered["表示"] = df_filtered.apply(format_past_row, axis=1)

    grouped = df_filtered.groupby("馬名")["表示"].apply(lambda x: x.tolist()[:5]).reset_index()
    df_past5 = grouped.set_index("馬名")["表示"].apply(pd.Series)
    df_past5.columns = [f"{i+1}走前" for i in range(df_past5.shape[1])]
    df_past5.reset_index(inplace=True)
    return df_past5
    with tab1:
    st.subheader("🔽 出走予定馬CSV & 出馬表CSVをアップロード")

    e_uploaded = st.file_uploader("出走予定馬CSV", type="csv", key="entry")
    s_uploaded = st.file_uploader("出馬表CSV（全馬）", type="csv", key="shutsuba")

    if e_uploaded and s_uploaded:
        df_entry = pd.read_csv(e_uploaded, encoding="utf-8-sig")
        df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")
        df_entry.columns = [col.strip() for col in df_entry.columns]
        df_shutsuba.columns = [col.strip() for col in df_shutsuba.columns]

        entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
        df_past5 = generate_past5_display(df_shutsuba, entry_names)
        df_merged = pd.merge(df_entry, df_past5, on="馬名", how="left")

        # 表示用レース名生成
        df_merged["表示レース名"] = (
            df_merged["開催地"].astype(str).str.strip() +
            df_merged["R"].astype(str).str.strip() + "R " +
            df_merged["レース名"].astype(str).str.strip()
        )

        races = df_merged["表示レース名"].dropna().unique().tolist()
        tabs = st.tabs(races)

        for i, race in enumerate(races):
            with tabs[i]:
                race_df = df_merged[df_merged["表示レース名"] == race].drop(
                    columns=["表示レース名", "レース名", "開催地", "R"]
                ).reset_index(drop=True)

                st.markdown(f"### 🏁 {race}")
                st.write("")

                # HTML表示
                st.write(
                    race_df.to_html(escape=False, index=False),
                    unsafe_allow_html=True
                )
                with tab2:
    st.subheader("✅ 確定出馬表CSVをアップロード")

    s_uploaded = st.file_uploader("確定出馬表CSV", type="csv", key="final")
    if s_uploaded:
        df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")
        st.success("✅ 確定出馬表（全馬）")
        st.dataframe(df_shutsuba)
