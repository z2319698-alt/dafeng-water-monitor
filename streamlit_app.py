import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統 V2", layout="wide")

# --- 質感深色 CSS & 字體放大設定 ---
st.markdown("""
    <style>
    /* 側邊欄背景與按鈕樣式 */
    [data-testid="stSidebar"] { background-color: #262730; }
    [data-testid="stSidebar"] .stMarkdown p { color: white !important; font-size: 18px !important; }
    
    .stButton > button {
        width: 100%; border-radius: 8px; height: 3.2em;
        background-color: #3e3f4b; color: #ffffff; border: 1px solid #4d4d4d;
        text-align: left; padding-left: 15px; margin-bottom: 5px;
        font-size: 16px !important;
    }
    .stButton > button:hover { border-color: #00d4ff; background-color: #4e505c; }
    
    /* 子項目按鈕樣式 (稍微縮進) */
    .sub-item > div > button {
        width: 90% !important; margin-left: 10% !important;
        background-color: #2c2d36 !important; height: 2.8em !important;
        font-size: 14px !important;
    }

    /* 放大指標卡文字 */
    [data-testid="stMetricValue"] { font-size: 40px !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { font-size: 20px !important; }
    
    /* 放大標題文字 */
    h1 { font-size: 42px !important; }
    h2 { font-size: 32px !important; }
    h3 { font-size: 26px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 導覽功能與狀態管理 ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1. 全興廢水水質資料"
if 'waste_expand' not in st.session_state:
    st.session_state.waste_expand = False

st.sidebar.title("🏠 系統導航")

# 主要按鈕定義
def nav_item(label, icon, is_sub=False):
    container = st.sidebar.container()
    if is_sub:
        with container:
            st.markdown('<div class="sub-item">', unsafe_allow_html=True)
            if st.button(f"{icon} {label}", key=f"btn_{label}"):
                st.session_state.current_page = label
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if container.button(f"{icon} {label}", key=f"btn_{label}"):
            st.session_state.current_page = label
            # 如果點擊的是廢棄物，則切換展開狀態
            if "廢棄物" in label:
                st.session_state.waste_expand = not st.session_state.waste_expand

# 逐一建立導覽項目
nav_item("1. 全興廢水水質資料", "🌊")
nav_item("2. 全興空污排放資料", "💨")
nav_item("3. 全興廢水水量統計", "📏")
nav_item("4. 每月衍生廢棄物量統計", "♻️")

# --- 廢棄物子選單 (當點擊第 4 項時展開) ---
if st.session_state.waste_expand or "廢塑膠" in st.session_state.current_page or "有機污泥" in st.session_state.current_page:
    nav_item("廢塑膠混合物統計", "📦", is_sub=True)
    nav_item("廢塑膠統計", "🧪", is_sub=True)
    nav_item("有機污泥統計", "🛢️", is_sub=True)

nav_item("5. 每月原物料量統計", "📦")
nav_item("6. 每月產品量統計", "🏭")

page = st.session_state.current_page
st.title(page)

# --- 數據抓取函數 (含圖表大字體優化) ---
def plot_big_chart(df, x, y, title, chart_type="line", color="#3498DB"):
    fig = None
    if chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title, markers=True)
    elif chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    
    # 強制放大圖表文字
    fig.update_layout(
        title_font_size=28,
        xaxis=dict(tickfont=dict(size=18), title_font=dict(size=20)),
        yaxis=dict(tickfont=dict(size=18), title_font=dict(size=20)),
        legend=dict(font=dict(size=18))
    )
    st.plotly_chart(fig, use_container_width=True)

def get_report_data_by_url(gid, rows_list, value_names):
    base_url = "https://docs.google.com/spreadsheets/d/13cbFM5KVoobPir_hZv5D0h8Wh5m--xKTv8uGLv-iNQc/edit#gid="
    target_url = f"{base_url}{gid}"
    full_df = conn.read(spreadsheet=target_url, ttl="0", header=None)
    dates = full_df.iloc[0, 1:].values
    mask = [str(d) >= "114.01" for d in dates]
    filtered_dates = [d for d, m in zip(dates, mask) if m]
    results = {"月份": filtered_dates}
    for row_idx, name in zip(rows_list, value_names):
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
        plot_big_chart(df, "月份", "廢水量(T)", "廢水量(T) 月度統計", "bar")

    elif "廢棄物" in page or "統計" in page:
        # 抓取三項資料
        df = get_report_data_by_url(REPORT_GID, [31, 36, 40], ["廢塑膠混合物", "廢塑膠", "有機污泥"])
        
        if page == "4. 每月衍生廢棄物量統計":
            st.info("請從左側選擇具體廢棄物項目以查看詳細報表。")
            plot_big_chart(df, "月份", ["廢塑膠混合物", "廢塑膠", "有機污泥"], "廢棄物總覽對照")
            
        elif page == "廢塑膠混合物統計":
            st.metric("當前產量 (A31)", f"{df['廢塑膠混合物'].iloc[-1]} T")
            plot_big_chart(df, "月份", "廢塑膠混合物", "廢塑膠混合物 (A31) 走勢", "bar", "#3498DB")
            
        elif page == "廢塑膠統計":
            st.metric("當前產量 (A36)", f"{df['廢塑膠'].iloc[-1]} T")
            plot_big_chart(df, "月份", "廢塑膠", "廢塑膠 (A36) 走勢", "bar", "#F1C40F")
            
        elif page == "有機污泥統計":
            st.metric("當前產量 (A40)", f"{df['有機污泥'].iloc[-1]} T")
            plot_big_chart(df, "月份", "有機污泥", "有機污泥 (A40) 走勢", "bar", "#E67E22")
        
        st.dataframe(df, use_container_width=True)

    elif page == "5. 每月原物料量統計":
        df = get_report_data_by_url(REPORT_GID, [26], ["原物料投入量"])
        plot_big_chart(df, "月份", "原物料投入量", "原物料投入趨勢", "line")

    elif page == "6. 每月產品量統計":
        df = get_report_data_by_url(REPORT_GID, [27, 28], ["塑膠碎片", "塑膠粒"])
        plot_big_chart(df, "月份", ["塑膠碎片", "塑膠粒"], "產品產出量對比", "bar")

except Exception as e:
    st.error(f"❌ 系統錯誤：{e}")
