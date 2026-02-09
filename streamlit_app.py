import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統 V2", layout="wide")

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

# --- 數據抓取函數 ---
def get_report_data_by_url(gid, rows_list, value_names):
    # 使用您的申報表網址
    base_url = "https://docs.google.com/spreadsheets/d/13cbFM5KVoobPir_hZv5D0h8Wh5m--xKTv8uGLv-iNQc/edit#gid="
    target_url = f"{base_url}{gid}"
    
    # 讀取資料
    full_df = conn.read(spreadsheet=target_url, ttl="0", header=None)
    
    # 提取第 1 列 (日期) 並篩選 114.01 以後
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
    REPORT_GID = "2023886467"

    if page == "1. 全興廢水水質資料":
        WATER_URL = "https://docs.google.com/spreadsheets/d/13cbFM5KVoobPir_hZv5D0h8Wh5m--xKTv8uGLv-iNQc/edit#gid=218818027"
        df = conn.read(spreadsheet=WATER_URL, ttl="0")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "3. 全興廢水水量統計":
        df = get_report_data_by_url(REPORT_GID, [30], ["廢水量(T)"])
        if not df.empty:
            st.bar_chart(df.set_index("月份"))
            st.dataframe(df, use_container_width=True)

    elif page == "4. 每月衍生廢棄物量統計":
        # 抓取 A31:廢塑膠混合物, A36:廢塑膠, A40:有機污泥
        df = get_report_data_by_url(REPORT_GID, [31, 36, 40], ["廢塑膠混合物", "廢塑膠", "有機污泥"])
        
        if not df.empty:
            # 頂部指標
            latest_month = df['月份'].iloc[-1]
            st.subheader(f"📅 {latest_month} 產出摘要")
            m1, m2, m3 = st.columns(3)
            m1.metric("廢塑膠混合物", f"{df['廢塑膠混合物'].iloc[-1]} T")
            m2.metric("廢塑膠", f"{df['廢塑膠'].iloc[-1]} T")
            m3.metric("有機污泥", f"{df['有機污泥'].iloc[-1]} T")
            
            st.markdown("---")
            # 細分頁籤
            tab_all, tab1, tab2, tab3 = st.tabs(["📊 總體對照", "📦 廢塑膠混合物", "🧪 廢塑膠", "🛢️ 有機污泥"])
            with tab_all:
                st.plotly_chart(px.line(df, x="月份", y=df.columns[1:], markers=True), use_container_width=True)
            with tab1:
                st.plotly_chart(px.bar(df, x="月份", y="廢塑膠混合物", color_discrete_sequence=['#3498DB']), use_container_width=True)
            with tab2:
                st.plotly_chart(px.bar(df, x="月份", y="廢塑膠", color_discrete_sequence=['#F1C40F']), use_container_width=True)
            with tab3:
                st.plotly_chart(px.bar(df, x="月份", y="有機污泥", color_discrete_sequence=['#E67E22']), use_container_width=True)

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
