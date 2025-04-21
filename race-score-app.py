import streamlit as st
import pandas as pd

st.set_page_config(page_title="出馬表フィルタ", layout="wide")
st.title("🐎 出馬表フィルタ - 出走段階切り替え対応")

tab1, tab2 = st.tabs(["🟩 出走予定馬（想定）", "🟦 枠順確定後（確定出馬）"])

# --------------------------
# 🟩 出走予定馬（想定）
# --------------------------
with tab1:
    st.subheader("🔽 出走予定馬CSV & 出馬表CSVをアップロード")

    e_uploaded = st.file_uploader("出走予定馬CSV", type="csv", key="entry")
    s_uploaded = st.file_uploader("出馬表CSV（全馬）", type="csv", key="shutsuba")

    if e_uploaded and s_uploaded:
        try:
            df_entry = pd.read_csv(e_uploaded, encoding="utf-8-sig")
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            try:
                df_entry = pd.read_csv(e_uploaded, encoding="shift_jis")
            except Exception:
                st.error("❌ 出走予定馬CSVの読み込みに失敗しました。")
                st.stop()

        try:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="utf-8-sig")
        except (UnicodeDecodeError, pd.errors.ParserError):
            try:
                df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")
            except Exception:
                st.error("❌ 出馬表CSVの読み込みに失敗しました。")
                st.stop()

        # .strip() で列名をきれいに整えて再設定
        df_entry.columns = [col.strip() for col in df_entry.columns]
        df_shutsuba.columns = [col.strip() for col in df_shutsuba.columns]

        # デバッグログ（Streamlit上に表示）
        st.write("📋 出走予定馬CSVの列名:", df_entry.columns.tolist())
        st.write("📋 出馬表CSVの列名:", df_shutsuba.columns.tolist())

        # 馬名列チェック
        if "馬名" in df_entry.columns and "馬名" in df_shutsuba.columns:
            entry_names = df_entry["馬名"].astype(str).str.strip().unique().tolist()
            df_filtered = df_shutsuba[df_shutsuba["馬名"].astype(str).str.strip().isin(entry_names)]

            st.success(f"✅ {len(df_filtered)}頭分のフィルタ済出馬表")
            st.dataframe(df_filtered)

            csv = df_filtered.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 フィルタ出馬表CSVをダウンロード", csv, file_name="フィルタ出馬表.csv")
        else:
            st.error("❌ '馬名' 列が見つかりませんでした。上記の列名リストを確認してください。")

# --------------------------
# 🟦 枠順確定後（確定出馬）
# --------------------------
with tab2:
    st.subheader("✅ 確定済み出馬表CSVをアップロード")

    s_uploaded = st.file_uploader("確定出馬表CSV", type="csv", key="final")

    if s_uploaded:
        try:
            df_shutsuba = pd.read_csv(s_uploaded, encoding="utf-8-sig")
        except (UnicodeDecodeError, pd.errors.ParserError):
            try:
                df_shutsuba = pd.read_csv(s_uploaded, encoding="shift_jis")
            except Exception:
                st.error("❌ 出馬表CSVの読み込みに失敗しました。")
                st.stop()

        st.success("✅ 確定出馬表を表示中")
        st.dataframe(df_shutsuba)

        csv = df_shutsuba.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 出馬表CSVをダウンロード", csv, file_name="確定出馬表.csv")
