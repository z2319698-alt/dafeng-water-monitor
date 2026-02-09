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

# 2. 建立連線 (指向申報總表的分頁)
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

# --- 核心數據抓取邏輯 ---
def get_report_data(rows_list, value_names):
    # 讀取「全興廠申報表_佳欣」分頁 
    raw_df = conn.read(worksheet="全興廠申報表_佳欣", ttl="0")
    
    # 提取第1列(A1)作為日期，並篩選 114.01 以後 
    dates = raw_df.iloc[0, 1:].values
    mask = [str(d) >= "114.01" for d in dates]
    filtered_dates = dates[mask]
    
    results = {"月份": filtered_dates}
    for row_idx, name in zip(rows_list, value_names):
        # 減 2 是因為 DataFrame index 從 0 開始且 Excel 與 DF 的偏移
        # 根據  的結構，我們精確定位列號
        vals = raw_df.iloc[row_idx-1, 1:].values[mask]
        results[name] = pd.to_numeric([str(v).replace(',', '') for v in vals], errors='coerce')
    
    return pd.DataFrame(results)

try:
    if page == "1. 全興廢水水質資料":
        df = conn.read(worksheet="水質記錄", ttl="0")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "3. 全興廢水水量統計":
        # 抓取 A30 (廢水量-納管排放) 
        df = get_report_data([30], ["廢水量(T)"])
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "4. 每月衍生廢棄物量統計":
        # 抓取 A31, A36, A40 
        df = get_report_data([31, 36, 40], ["廢塑膠混合物", "R-0201產出", "有機污泥"])
        fig = px.line(df, x="月份", y=df.columns[1:], markers=True, title="廢棄物趨勢")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    elif page == "5. 每月原物料量統計":
        # 抓取 A26 (瓶磚-投入量) 
        df = get_report_data([26], ["原物料投入量"])
        st.area_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

    elif page == "6. 每月產品量統計":
        # 抓取 A27, A28 (塑膠碎片產出量、粒) 
        df = get_report_data([27, 28], ["塑膠碎片(粉)", "塑膠粒"])
        st.bar_chart(df.set_index("月份"))
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"數據對接失敗，請檢查 Excel 分頁名稱是否為『全興廠申報表_佳欣』。錯誤訊息: {e}")
