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

# --- 數據抓取函數 (使用 URL 直接鎖定分頁，避免 Index 錯誤) ---
def get_report_data_by_url(gid, rows_list, value_names):
    # 這裡使用您提供的申報表網址，並強制指定 gid (分頁 ID)
    base_url = "https://docs.google.com/spreadsheets/d/13cbFM5KVoobPir_hZv5D0h8Wh5m--xKTv8uGLv-iNQc/edit#gid="
    target_url = f"{base_url}{gid}"
    
    # 讀取資料
    full_df = conn.read(spreadsheet=target_url, ttl="0", header=None)
    
    # 檢查列數是否足夠
    max_row_needed = max(rows_list)
    if len(full_df) < max_row_needed:
        st.error(f"表格列數不足！需要到第 {max_row_needed} 列，但目前只有 {len(full_df)} 列。")
        return pd.DataFrame()

    # 1. 提取第 1 列 (日期) 並篩選 114.01 以後
    # 第 1 列在 DataFrame 是 index 0
    dates = full_df.iloc[0, 1:].values
    mask = [str(d) >= "114.01" for d in dates]
    filtered_dates = [d for d, m in zip(dates, mask) if m]
    
    results = {"月份": filtered_dates}
    for row_idx, name in zip(rows_list, value_names):
        # Excel 第 N 列在 DataFrame 是 Index N-1
        vals = full_df.iloc[row_idx-1, 1:].values
        filtered_vals = [str(v).replace(',', '') for v, m in zip(vals, mask) if m]
        results[name] = pd.to_numeric(filtered_vals, errors='coerce')
    
    return pd.DataFrame(results)

# --- 頁面邏輯 ---
try:
    # 申報表分頁的 GID (根據您提供的網址是 2023886467)
    REPORT_GID = "2023886467"

    if page == "1. 全興廢水水質資料":
        # 水質記錄分頁 (GID 是 218818027)
        WATER_URL = "https://docs.google.com/spreadsheets/d/13cbFM5KVoobPir_hZv5D0h8Wh5m--xKTv8uGLv-iNQc/edit#gid=218818027"
        df = conn.read(spreadsheet=WATER_URL, ttl="0")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "3. 全興廢水水量統計":
        df = get_report_data_by_url(REPORT_GID, [30], ["廢水量(T)"])
        if not df.empty:
            st.bar_chart(df.set_index("月份"))
            st.dataframe(df, use_container_width=True)

    elif page == "4. 每月衍生廢棄物量統計":
        df = get_report_data_by_url(REPORT_GID, [31, 36, 40], ["廢塑膠混合物", "再利用產出", "有機污泥"])
        if not df.empty:
            fig = px.line(df, x="月份", y=df.columns[1:], markers=True)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

    elif page == "5. 每月原物料量統計":
        df = get_report_data_by_url(REPORT_GID, [26], ["原物料投入量"])
        if not df.empty:
            st.area_chart(df.set_index("月份"))
            st.dataframe(df, use_container_width=True)

    elif page == "6. 每月產品量統計":
        df = get_report_data_by_url(REPORT_GID, [27, 28], ["塑膠碎片", "塑膠粒"])
        if not df.empty:
            st.bar_chart(df.set_index("月份"))
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ 系統錯誤：{e}")
