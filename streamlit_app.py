import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統", layout="wide")

# --- 修改後的深色 CSS：讓背景變深，按鈕更有質感 ---
st.markdown("""
    <style>
    /* 1. 讓側邊欄背景變為深灰色 (像 image_3f6238.png 那樣) */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* 2. 調整側邊欄所有文字為白色 */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1 {
        color: white !important;
    }

    /* 3. 按鈕外觀調整 (深色底、白字、細邊框) */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #3e3f4b; /* 深灰按鈕底色 */
        color: #ffffff;            /* 白色文字 */
        border: 1px solid #4d4d4d;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        text-align: left;
        padding-left: 15px;
        margin-bottom: 10px;
    }

    /* 4. 滑鼠移上去的變色效果 (亮藍色或綠色邊框) */
    .stButton > button:hover {
        border-color: #00d4ff;
        background-color: #4e505c;
        color: #ffffff;
        transform: translateY(-1px);
    }

    /* 5. 隱藏預設的單選標記 */
    div[role="radiogroup"] {
        display: none;
    }
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

# 獲取目前選定頁面並顯示內容
page = st.session_state.current_page
st.title(page)

# --- 數據處理邏輯 ---
try:
    df = conn.read(ttl="0")

    if page == "1. 全興廢水水質資料":
        # 對應 Excel 實際欄位
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
        st.info(f"💡 【{page}】內容建置中...")

except Exception as e:
    st.error(f"❌ 數據載入失敗：{e}")
