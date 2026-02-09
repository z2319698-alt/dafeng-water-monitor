import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 設定網頁標題
st.set_page_config(page_title="全興廠水質監測系統", layout="wide")

st.title("🌊 全興廠水質監測儀表板")

# 1. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. 讀取數據 (請確保試算表分頁名稱叫 "水質記錄")
try:
    # 這裡會從 Secrets 抓取 URL
    df = conn.read(worksheet="水質記錄")
    
    # 清洗數據：將數值轉為數字，避免圖表出錯
    cols = ['COD', 'SS', 'PH', '溫度']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 介面佈局 ---
    tab1, tab2 = st.tabs(["📊 數據總覽", "📈 趨勢分析"])

    with tab1:
        st.subheader("📋 最新檢測數據表")
        # 顯示最新數據在最上方
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
        # 下載按鈕
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載完整資料 (CSV)", csv, "water_report.csv", "text/csv")

    with tab2:
        st.subheader("📈 檢測數值走勢")
        if not df.empty and '日期' in df.columns:
            target = st.selectbox("選擇觀察項目", cols)
            fig = px.line(df, x="日期", y=target, title=f"{target} 歷史走勢", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("目前尚無足夠數據繪製圖表。")

    st.success("✅ 數據連線正常")

except Exception as e:
    st.error(f"❌ 連線失敗：{e}")
    st.info("請檢查 Streamlit Secrets 設定是否正確。")
