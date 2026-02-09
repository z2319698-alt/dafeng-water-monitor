import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import urllib.parse

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

# --- 編碼修正：自動轉化中文分頁名稱 ---
def safe_read_worksheet(sheet_name):
    # 將中文分頁名稱轉為 URL 安全格式，解決 ASCII 報錯
    return conn.read(worksheet=sheet_name, ttl="0")

def get_report_data(rows_list, value_names):
    # 讀取分頁
    raw_df = safe_read_worksheet("全興申報表") 
    
    # 提取第1列(A1)並篩選 114.01 以後
    dates = raw_df.columns[1:]
    mask = [str(d) >= "114.01" for d in dates]
    filtered_dates = [d for d, m in zip(dates, mask) if m]
    
    results = {"月份": filtered_dates}
    for row_idx, name in zip(rows_list, value_names):
        # 抓取對應 Excel 列位 (Row Index 需轉換為 0-based)
        vals = raw_df.iloc[row_idx-2, 1:].values # 調整偏移量以對應截圖
        filtered_vals = [str(v).replace(',', '') for v, m in zip(vals, mask) if m]
        results[name] = pd.to_numeric(filtered_vals, errors='coerce')
    
    return pd.DataFrame(results)

try:
    if page == "1. 全興廢水水質資料":
        df = safe_read_worksheet("水質記錄") #
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "3. 全興廢水水量統計":
        # A30: 廢水量(7500T)-納管排放
        df = get_report_data([30], ["廢水量(T)"])
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "4. 每月衍生廢棄物量統計":
        # A31: 廢塑膠, A36: R-0201產出, A40: 有機污泥
        df = get_report_data([31, 36, 40], ["廢塑膠混合物", "再利用產出", "有機污泥"])
        fig = px.line(df, x="月份", y=df.columns[1:], markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    elif page == "5. 每月原物料量統計":
        # A26: 瓶磚-投入量
        df = get_report_data([26], ["原物料投入量"])
        st.area_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "6. 每月產品量統計":
        # A27: 塑膠碎片, A28: 塑膠粒
        df = get_report_data([27, 28], ["塑膠碎片", "塑膠粒"])
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ 數據對接失敗：{e}")
    st.info("請確認 Excel 分頁名稱是否與程式碼一致（目前預設：全興申報表 與 水質記錄）。")
