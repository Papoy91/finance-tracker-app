import streamlit as st
from utils.gsheet import load_data

st.set_page_config(page_title="Monthly Finance Tracker", layout="wide")
st.title("📊 Monthly Financial Tracker")

st.markdown("""
Welcome to the Monthly Financial Tracker App.
Use the sidebar to navigate between **Data Entry** and **Charts/Analysis** pages.
""")