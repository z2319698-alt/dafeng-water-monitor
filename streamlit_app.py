import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="全興廠水質監測", layout="wide")
st.title("🌊 全興廠水質監測自動化")

# 建立與 Google Sheets 的連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取你的試算表數據
# 注意：這裡的 URL 稍後我們要設定在 Secrets 裡，現在先寫最基礎的測試
try:
    df = conn.read(worksheet="水質記錄")
    st.success("✅ 數據連線成功！")
    st.dataframe(df)
except Exception as e:
    st.warning("⏳ 正在等待資料權限設定...請先完成 Secrets 設定。")
