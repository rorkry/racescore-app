import streamlit as st
import pandas as pd

st.set_page_config(page_title="📋 レースレベル確認", layout="wide")
st.title("🧪 出馬表CSVのレースレベル（G列）確認テスト")

# ファイルアップロード
shutsuba_csv = st.file_uploader("📤 出馬表.csv（G列にレースレベル）", type="csv")

if shutsuba_csv:
    df = pd.read_csv(shutsuba_csv, encoding="shift_jis")
    df.columns = [col.strip() for col in df.columns]
    
    st.write("📋 読み込まれた列一覧:", df.columns.tolist())

    # G列の取得
    try:
        level_col = df.columns[6]
        st.success(f"✅ G列の列名：{level_col}")

        unique_levels = df[level_col].astype(str).unique()
        st.write("🧪 G列のユニークな値（元の値）:", unique_levels)

        # レースレベルを★に変換（全角対応）
        def level_to_star(lv):
            lv = str(lv).strip().replace("Ａ", "A").replace("Ｂ", "B").replace("Ｃ", "C").replace("Ｄ", "D").replace("Ｅ", "E")
            return {
                "A": "★★★★★",
                "B": "★★★★☆",
                "C": "★★★☆☆",
                "D": "★★☆☆☆",
                "E": "★☆☆☆☆",
            }.get(lv, "ー")

        df["★"] = df[level_col].map(level_to_star)
        st.write("📝 サンプル表示（馬名・レースレベル・★）")
        st.dataframe(df[[df.columns[4], level_col, "★"]].head(10))  # 馬名・レベル・★

    except Exception as e:
        st.error(f"❌ G列の取得に失敗しました: {e}")
else:
    st.info("🔽 出馬表CSVをアップロードしてください。")
