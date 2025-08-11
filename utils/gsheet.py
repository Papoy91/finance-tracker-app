import gspread
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_resource
def connect_sheet():
    if "google_cloud" not in st.secrets:
        st.error("❌ Google Cloud credentials not found in secrets.")
        st.stop()

    creds_dict = st.secrets["google_cloud"]
    credentials = service_account.Credentials.from_service_account_info(dict(creds_dict))
    scoped_credentials = credentials.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(scoped_credentials)
    sheet = client.open("finance_tracker").worksheet("data")
    return sheet

@st.cache_data
def load_data():
    sheet = connect_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df
