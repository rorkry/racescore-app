def display_race_table(df, race_label):
    for idx, row in df.iterrows():
        st.markdown(f"✅ DEBUG: {row['馬名']} 表示中（印・メモなし）")

        col1, col2, col3 = st.columns([0.3, 2, 12])

        # 印の削除 → col1は空白用として維持
        with col1:
            st.markdown("&nbsp;", unsafe_allow_html=True)

        # 馬名・馬柱
        with col2:
            st.markdown(f"<div style='text-align:center; font-weight:bold; color:{TEXT_COLOR};'>{row['馬名']}<br><span style='font-size:11px'>{row['性別']}{row['年齢']}・{row['斤量']}kg</span></div>", unsafe_allow_html=True)

        with col3:
            html_row = "<table style='width:100%; text-align:center; border-spacing:0'><tr>"
            for col in [f"{i}走前" for i in range(1, 6)]:
                html = row[col] if pd.notnull(row[col]) else f"<div style='min-height:100px; color:{TEXT_COLOR};'>ー</div>"
                html_row += f"<td style='vertical-align:top; min-width:140px'>{html}</td>"
            html_row += "</tr></table>"
            st.markdown(html_row, unsafe_allow_html=True)
