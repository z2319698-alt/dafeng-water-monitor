import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="全興廠自動化監測系統", layout="wide")

# 2. 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 側邊欄：多頁面導覽設計 ---
st.sidebar.title("🏢 全興廠管理系統")
st.sidebar.subheader("數據監測中心")

page = st.sidebar.selectbox(
    "請選擇導覽項目",
    [
        "1. 全興廢水水質資料",
        "2. 全興空污排放資料",
        "3. 全興廢水水量統計",
        "4. 每月衍生廢棄物量統計",
        "5. 每月原物料量統計",
        "6. 每月產品量統計"
    ]
)

# 顯示目前位置
st.title(page)

# --- 數據處理與顯示邏輯 ---
try:
    # 預設讀取 Excel (我們會根據不同的頁面來決定讀取哪個分頁)
    # 目前先以「水質記錄」作為基準，若您其他項目有獨立分頁，之後可以再調整程式碼
    df = conn.read(ttl="0")

    if page == "1. 全興廢水水質資料":
        # 欄位重新命名對應 (根據您的 Excel 標題)
        cols_map = {"檢測項COD": "COD", "檢測項目SS": "SS", "檢測項目PH": "PH", "檢測項目溫度": "溫度"}
        df_view = df.rename(columns=cols_map)

        tab1, tab2 = st.tabs(["📊 數據總覽", "📈 趨勢分析"])
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
        st.info("💡 系統提示：此模組正等待空污自動化腳本串接。")
        st.warning("請確保 Excel 中包含「空污記錄」分頁。")
        # 這裡未來可以寫成: df_air = conn.read(worksheet="空污記錄")

    elif page == "3. 全興廢水水量統計":
        st.info("💡 系統提示：目前正在分析每日廢水流量計數值。")
        # 這裡未來可以顯示長條圖 (Bar Chart) 比較每日流量

    elif page in ["4. 每月衍生廢棄物量統計", "5. 每月原物料量統計", "6. 每月產品量統計"]:
        st.subheader("📊 月度統計摘要")
        st.info(f"💡 系統提示：這是「{page[2:]}」的專屬統計頁面。")
        st.write("建議格式：請在 Excel 中建立對應名稱的分頁，欄位包含「月份」與「數量」。")
        # 顯示一個簡單的表格樣板
        sample_data = pd.DataFrame({"月份": ["2026/01", "2026/02"], "數值": [0, 0]})
        st.write("目前的資料範例：")
        st.table(sample_data)

except Exception as e:
    st.error(f"❌ 數據分流失敗：{e}")
    st.info("可能是因為 Excel 的分頁名稱不匹配，或網路連線不穩。")

# --- 頁尾資訊 ---
st.sidebar.markdown("---")
st.sidebar.caption(f"最後連線時間：{pd.Timestamp.now().strftime('%H:%M:%S')}")
st.sidebar.write("👤 登入身份：全興廠管理員")
