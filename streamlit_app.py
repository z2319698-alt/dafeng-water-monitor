import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統", layout="wide")

# --- 自定義 CSS：打造高質感按鈕 ---
st.markdown("""
    <style>
    /* 側邊欄整體背景稍微加深 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    /* 自定義按鈕樣式 */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ffffff;
        color: #31333F;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: left;
        padding-left: 20px;
        margin-bottom: 10px;
    }
    /* 懸停效果 */
    .stButton > button:hover {
        border-color: #4CAF50;
        color: #4CAF50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    /* 選中狀態的模擬 (透過 Session State) */
    </style>
    """, unsafe_allow_html=True)

# 2. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 側邊欄：質感按鈕導覽列 ---
st.sidebar.title("🏠 系統導航")
st.sidebar.markdown("---")

# 初始化頁面狀態
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 全興廢水水質資料"

# 定義導覽按鈕
def nav_button(label, icon):
    if st.sidebar.button(f"{icon} {label}"):
        st.session_state.current_page = label

# 逐一建立按鈕
nav_button("1. 全興廢水水質資料", "🌊")
nav_button("2. 全興空污排放資料", "💨")
nav_button("3. 全興廢水水量統計", "📏")
nav_button("4. 每月衍生廢棄物量統計", "♻️")
nav_button("5. 每月原物料量統計", "📦")
nav_button("6. 每月產品量統計", "🏭")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 更新資料庫"):
    st.cache_data.clear()
    st.rerun()

# 獲取目前選定頁面
page = st.session_state.current_page
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

    else:
        st.info(f"💡 系統提示：【{page}】模組已建立，目前等待數據資料夾串接。")
        st.write("請確保 Excel 中有對應的分頁名稱。")

except Exception as e:
    st.error(f"❌ 數據連線失敗：{e}")

# 頁尾資訊
st.sidebar.caption(f"系統狀態：運行中")
