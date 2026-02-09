import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠監測系統 V2", layout="wide")

# --- 質感深色 CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #262730; }
    [data-testid="stSidebar"] .stMarkdown p { color: white !important; }
    .stButton > button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #3e3f4b; color: #ffffff; border: 1px solid #4d4d4d;
        text-align: left; padding-left: 15px; margin-bottom: 10px;
    }
    .stButton > button:hover { border-color: #00d4ff; background-color: #4e505c; }
    </style>
    """, unsafe_allow_html=True)

# 2. 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 導覽功能 ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 全興廢水水質資料"

def nav_item(label, icon):
    if st.sidebar.button(f"{icon} {label}"):
        st.session_state.current_page = label

st.sidebar.title("🏠 系統導航")
nav_item("1. 全興廢水水質資料", "🌊")
nav_item("2. 全興空污排放資料", "💨")
nav_item("3. 全興廢水水量統計", "📏")
nav_item("4. 每月衍生廢棄物量統計", "♻️")
nav_item("5. 每月原物料量統計", "📦")
nav_item("6. 每月產品量統計", "🏭")

page = st.session_state.current_page
st.title(page)

# --- 核心數據抓取邏輯 (避開編碼報錯版) ---
def get_data_from_sheet(sheet_index, rows_list=None, value_names=None, mode="normal"):
    # 讀取整份 Excel
    all_data = conn.read(ttl="0") 
    # 如果有多個分頁，Streamlit 會讀取第一個。
    # 這裡我們採用最保險的做法：直接讀取，並根據傳入的模式處理。
    
    if mode == "report":
        # 處理「全興廠申報表」數據
        # 1. 提取日期列 (A1) 並篩選 114.01 以後
        dates = all_data.iloc[0, 1:].values
        mask = [str(d) >= "114.01" for d in dates]
        filtered_dates = dates[mask]
        
        results = {"月份": filtered_dates}
        for row_idx, name in zip(rows_list, value_names):
            # Excel 第 n 列在 DataFrame index 為 n-1 (因為 A1 是第 0 列)
            # 這裡根據您的截圖 A30 就是 index 29
            vals = all_data.iloc[row_idx-1, 1:].values[mask]
            results[name] = pd.to_numeric([str(v).replace(',', '') for v in vals], errors='coerce')
        return pd.DataFrame(results)
    else:
        # 處理「水質記錄」數據 (一般表格)
        return all_data

try:
    if page == "1. 全興廢水水質資料":
        # 預設抓取第一張工作表
        df = conn.read(ttl="0")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "3. 全興廢水水量統計":
        # 抓取 A30
        df = get_data_from_sheet(sheet_index=0, rows_list=[30], value_names=["廢水量(T)"], mode="report")
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "4. 每月衍生廢棄物量統計":
        # 抓取 A31, A36, A40
        df = get_data_from_sheet(sheet_index=0, rows_list=[31, 36, 40], 
                                 value_names=["廢塑膠混合物", "再利用產出", "有機污泥"], mode="report")
        fig = px.line(df, x="月份", y=df.columns[1:], markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    elif page == "5. 每月原物料量統計":
        # 抓取 A26
        df = get_data_from_sheet(sheet_index=0, rows_list=[26], value_names=["原物料投入量"], mode="report")
        st.area_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "6. 每月產品量統計":
        # 抓取 A27, A28
        df = get_data_from_sheet(sheet_index=0, rows_list=[27, 28], 
                                 value_names=["塑膠碎片", "塑膠粒"], mode="report")
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ 數據連線失敗：{e}")
    st.info("請確認您的 Google Sheets 網址是否正確，且第一個分頁為『全興廠申報表』。")
