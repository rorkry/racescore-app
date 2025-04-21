import streamlit as st
import pandas as pd

st.title("🐎 出馬表フィルタ - 出走段階切り替え対応")

# 📌 表示モード選択
mode = st.radio("📊 表示モードを選択", ["出走予定馬（想定）", "枠順確定後（確定出馬）"])

# ========================================
# 出走予定馬ベースの出馬表表示
# ========================================
if mode == "出走予定馬（想定）":
    st.subheader("🔽 出走予定馬CSV & 出馬表CSVをアップロード")

    e_uploaded = st.file_uploader("出走予定馬CSV", type="csv", key="entry")
    s_uploaded = st.file_uploader("出馬表CSV（全馬）", type="csv", key="shutsuba")

    if e_uploaded and s_uploaded:
        try:
            df_entry = pd.read_csv(e_uploaded, encoding="utf-8")
        except UnicodeDecodeError:
            df_entry = pd.read_csv(e_uploaded, encoding="shift_jis")

        try:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="utf-8")
        except UnicodeDecodeError:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")

        # 馬名列の自動検出
        entry_name_col = [col for col in df_entry.columns if "馬" in col and "名" in col]
        shutsuba_name_col = [col for col in df_shutsuba.columns if "馬" in col and "名" in col]

        if entry_name_col and shutsuba_name_col:
            entry_names = df_entry[entry_name_col[0]].astype(str).str.strip().unique().tolist()
            df_filtered = df_shutsuba[df_shutsuba[shutsuba_name_col[0]].astype(str).str.strip().isin(entry_names)]

            st.success(f"✅ {len(df_filtered)}頭分のフィルタ済出馬表")
            st.dataframe(df_filtered)

            # ダウンロードボタン
            csv = df_filtered.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 フィルタ出馬表CSVをダウンロード", csv, file_name="フィルタ出馬表.csv")
        else:
            st.error("❌ '馬名' 列が見つかりませんでした")

# ========================================
# 枠順確定後の出馬表を表示
# ========================================
elif mode == "枠順確定後（確定出馬）":
    st.subheader("✅ 確定済み出馬表CSVをアップロード")

    s_uploaded = st.file_uploader("確定出馬表CSV", type="csv", key="final")

    if s_uploaded:
        try:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="utf-8")
        except UnicodeDecodeError:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")

        st.success("✅ 確定出馬表を表示中")
        st.dataframe(df_shutsuba)

        csv = df_shutsuba.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 出馬表CSVをダウンロード", csv, file_name="確定出馬表.csv")
