import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="全興廠水質監測系統", layout="wide")
st.title("🌊 全興廠水質監測儀表板")

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 讀取分頁：水質記錄
    df = conn.read(worksheet="水質記錄", ttl="0")
    
    # 數值轉換，避免圖表出錯
    # 我們先印出欄位名稱來確認
    st.success("✅ 數據同步成功")
    
    # 側邊欄過濾功能
    st.sidebar.header("功能選單")
    item = st.sidebar.selectbox("選擇監測項目", ["COD", "SS", "PH", "溫度"])

    tab1, tab2 = st.tabs(["📊 數據總覽", "📈 趨勢圖表"])

    with tab1:
        st.subheader("📋 最新檢測數據 (由新到舊)")
        # 顯示最新數據
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
    with tab2:
        st.subheader(f"📈 {item} 歷史走勢")
        # 繪圖
        fig = px.line(df, x="日期", y=item, title=f"{item} 走勢圖", markers=True)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ 連線失敗：{e}")
    st.info("請確認 Secrets 裡的網址是否正確，且 Excel 的分頁名稱是否為 '水質記錄'。")
