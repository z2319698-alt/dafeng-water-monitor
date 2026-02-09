import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="全興廠水質監測系統", layout="wide")
st.title("🌊 全興廠水質監測儀表板")

# 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # --- 修改重點：不要在 read 裡面寫中文，直接讀取預設工作表 ---
    df = conn.read(ttl="0") 
    
    st.success("✅ 數據同步成功")

    # 對應你 Excel 裡的實際欄位名稱
    # 這裡要跟圖片裡的標題一模一樣
    cols_map = {
        "檢測項COD": "COD",
        "檢測項目SS": "SS",
        "檢測項目PH": "PH",
        "檢測項目溫度": "溫度"
    }
    
    # 重新命名欄位方便畫圖
    df = df.rename(columns=cols_map)

    tab1, tab2 = st.tabs(["📊 數據總覽", "📈 趨勢分析"])

    with tab1:
        st.subheader("📋 最新檢測數據 (由新到舊)")
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
    with tab2:
        st.subheader("📈 歷史走勢圖")
        # 只選擇有轉換成功的數值欄位
        available_cols = [c for c in ["COD", "SS", "PH", "溫度"] if c in df.columns]
        target = st.selectbox("選擇監測項目", available_cols)
        
        # 轉換為數字格式確保繪圖正常
        df[target] = pd.to_numeric(df[target], errors='coerce')
        
        fig = px.line(df, x="日期", y=target, title=f"{target} 趨勢", markers=True)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ 系統錯誤：{e}")
    st.info("請確認 Secrets 裡的網址後面沒有多餘的中文字。")
