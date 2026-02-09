elif page == "4. 每月衍生廢棄物量統計":
        # 抓取 A31:廢塑膠混合物, A36:廢塑膠, A40:有機污泥
        df = get_report_data_by_url(REPORT_GID, [31, 36, 40], ["廢塑膠混合物", "廢塑膠", "有機污泥"])
        
        if not df.empty:
            # --- 1. 頂部快報 (最新月份數值) ---
            latest_month = df['月份'].iloc[-1]
            st.subheader(f"📅 {latest_month} 廢棄物產出摘要")
            m1, m2, m3 = st.columns(3)
            m1.metric("廢塑膠混合物", f"{df['廢塑膠混合物'].iloc[-1]} T")
            m2.metric("廢塑膠", f"{df['廢塑膠'].iloc[-1]} T")
            m3.metric("有機污泥", f"{df['有機污泥'].iloc[-1]} T")
            
            st.markdown("---")

            # --- 2. 細分項目展示 ---
            tab_all, tab_mix, tab_plastic, tab_sludge = st.tabs(["📊 總體對照", "📦 廢塑膠混合物", "🧪 廢塑膠", "🛢️ 有機污泥"])
            
            with tab_all:
                st.write("三項指標趨勢對照 (114.01 起)")
                fig_all = px.line(df, x="月份", y=["廢塑膠混合物", "廢塑膠", "有機污泥"], 
                                  markers=True, template="plotly_dark")
                st.plotly_chart(fig_all, use_container_width=True)
            
            with tab_mix:
                st.write("廢塑膠混合物 (A31) 月度產量")
                fig_m = px.bar(df, x="月份", y="廢塑膠混合物", color_discrete_sequence=['#3498DB'])
                st.plotly_chart(fig_m, use_container_width=True)
                
            with tab_plastic:
                st.write("廢塑膠 (A36) 月度產量")
                fig_p = px.bar(df, x="月份", y="廢塑膠", color_discrete_sequence=['#F1C40F'])
                st.plotly_chart(fig_p, use_container_width=True)
                
            with tab_sludge:
                st.write("有機污泥 (A40) 月度產量")
                fig_s = px.bar(df, x="月份", y="有機污泥", color_discrete_sequence=['#E67E22'])
                st.plotly_chart(fig_s, use_container_width=True)

            # 數據表呈現
            with st.expander("🔎 查看詳細數據表"):
                st.dataframe(df, use_container_width=True)
