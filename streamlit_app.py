import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統", layout="wide")

# 2. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 側邊欄：一目了然導覽列 ---
st.sidebar.title("🏢 全興廠監測中心")
st.sidebar.markdown("---")

# 將項目逐一列出
page = st.sidebar.radio(
    "📊 數據監測項目清單",
    [
        "1. 全興廢水水質資料",
        "2. 全興空污排放資料",
        "3. 全興廢水水量統計",
        "4. 每月衍生廢棄物量統計",
        "5. 每月原物料量統計",
        "6. 每月產品量統計"
    ],
    index=0 # 預設停在第一個
)

st.sidebar.markdown("---")

# 顯示目前頁面標題
st.title(page)

# --- 數據處理邏輯 ---
try:
    # 讀取 Excel 數據
    df = conn.read(ttl="0")

    if page == "1. 全興廢水水質資料":
        # 欄位重新命名對應
        cols_map = {"檢測項COD": "COD", "檢測項目SS": "SS", "檢測項目PH": "PH", "檢測項目溫度": "溫度"}
        df_view = df.rename(columns=cols_map)

        tab1, tab2 = st.tabs(["📋 數據總覽", "📈 趨勢分析"])
        with tab1:
            st.dataframe(df_view.iloc[::-1], use_container_width=True)
        with tab2:
            items = ["COD", "SS", "PH", "溫度"]
            available = [c for c in items if c in df_view.columns]
            target = st.selectbox("選擇監測指標", available)
            df_view[target] = pd.to_numeric(df_view[target], errors='coerce')
            fig = px.line(df_view, x="日期", y=target, title=f"{target} 歷史走勢", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    elif page == "2. 全興空污排放資料":
        st.info("💨 此模組正等待空污自動化腳本 (Gmail OCR) 串接數據。")
        st.write("目前狀態：待機中")

    elif page == "3. 全興廢水水量統計":
        st.info("📏 每日進流水與放流水量統計模組。")
        st.write("目前狀態：待機中")

    elif page == "4. 每月衍生廢棄物量統計":
        st.info("♻️ 每月廢油、廢淤泥、一般垃圾產量統計。")
        st.write("目前狀態：待機中")

    elif page == "5. 每月原物料量統計":
        st.info("📦 每月藥劑、燃料、生產原料消耗量。")
        st.write("目前狀態：待機中")

    elif page == "6. 每月產品量統計":
        st.info("🏭 每月成品產出量統計。")
        st.write("目前狀態：待機中")

except Exception as e:
    st.error(f"❌ 數據載入失敗：{e}")

# --- 側邊欄底端資訊 ---
st.sidebar.markdown("---")
st.sidebar.caption(f"系統運行中 - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
