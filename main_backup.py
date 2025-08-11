import streamlit as st
from datetime import date

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px


# Fetch data from Google Sheet into DataFrame
def load_data():
    sheet = connect_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


if "google_cloud" in st.secrets:
    creds_dict = st.secrets["google_cloud"]
else:
    st.error("❌ Google Cloud credentials not found in secrets.")

creds_dict = st.secrets["google_cloud"]
credentials = service_account.Credentials.from_service_account_info(dict(creds_dict))

# Connect to Google Sheet
@st.cache_resource
def connect_sheet():
    scoped_credentials = credentials.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(scoped_credentials)
    sheet = client.open("finance_tracker").worksheet("data")
    return sheet


st.set_page_config(page_title="Monthly Finance Tracker", layout="wide")
st.title("📊 Monthly Financial Tracker")

# Section Selector
section = st.sidebar.selectbox("Select Section", ["USA", "India"])

# Category Dropdown
category = st.selectbox("Select Category", ["Earning", "Expense", "Invest", "Transfer"])

# Subcategories based on selection
subcategory_options = {
    "USA": {
        "Earning": ["Salary", "Award"],
        "Expense": ["Rent", "Grocery", "Restaurant", "Trip", "Mobile recharge",
                    "Ciggrets", "Drinks", "Entertainment", "Cab", "Transport", "Utilities",
                    "Cash Withdraw", "Home loan", "Other"],
        "Transfer": ["To India account", "Other"]
    },
    "India": {
        "Earning": ["Money Transfer USA", "Freelancing", "Interest", "Stock", "Other"],
        "Expense": ["Home loan", "Grocery", "Maid", "E/B", "Mobile recharge",
                    "Cab", "Garments", "Daughter", "Amazon", "Credit card", "Utilities", "Other"],
        "Invest": ["Mutual Fund", "Stock", "Insurance premium", "Term Insurance", "Fixed diposit", "Other"],
        "Transfer": ["To India account", "Other"]
    }
}

# Check if the category is valid for selected section
subcategory_list = subcategory_options.get(section, {}).get(category, [])
if not subcategory_list:
    st.warning("This category is not available in the selected section.")
else:
    subcategory = st.selectbox("Select Subcategory", subcategory_list)
    # Show note if 'Other' is selected
    note = ""
    if subcategory == "Other":
        note = st.text_input("Enter custom note")

    # Show amount input
    amount = st.number_input("Enter Amount", min_value=0.0, format="%.2f")

    # Date field
    entry_date = st.date_input("Date", value=date.today())
    currency = ""
    if section == "USA":
        currency = "$"
    else:
        currency = "₹"
    if st.button("Submit Entry"):
        sheet = connect_sheet()
        row = [str(entry_date), section, category, subcategory, note, amount]
        sheet.append_row(row)
        st.success("✅ Entry saved to Google Sheet!")
        if subcategory == "Other":
            st.success(f"Saved: {section} - {category} - {subcategory} - {note} - {currency} {amount} on {entry_date}")
        else:
            st.success(f"Saved: {section} - {category} - {subcategory} - {currency} {amount} on {entry_date}")


st.header("📈 Financial Summary & Charts")
df = load_data()

# Filters
with st.expander("🔍 Filter Data"):
    selected_section = st.multiselect("Section", options=df["Section"].unique(), default=list(df["Section"].unique()))
    selected_category = st.multiselect("Category", options=df["Category"].unique(), default=list(df["Category"].unique()))
    date_range = st.date_input("Date Range", value=[df["Date"].min(), df["Date"].max()])

# Apply filters
filtered_df = df[
    (df["Section"].isin(selected_section)) &
    (df["Category"].isin(selected_category)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# Summary Metrics
total_earning = filtered_df[filtered_df["Category"] == "Earning"]["Amount"].sum()
total_expense = filtered_df[filtered_df["Category"] == "Expense"]["Amount"].sum()
total_transfer = filtered_df[filtered_df["Category"] == "Transfer"]["Amount"].sum()
net_balance = total_earning - total_expense

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Earning", f"${total_earning:,.2f}")
col2.metric("💸 Total Expense", f"${total_expense:,.2f}")
col3.metric("🔁 Total Transfer", f"${total_transfer:,.2f}")
col4.metric("📉 Net Balance", f"${net_balance:,.2f}")

# Charts
if not filtered_df.empty:
    st.subheader("📊 Expense Breakdown")
    pie_df = filtered_df[filtered_df["Category"] == "Expense"].groupby("Subcategory")["Amount"].sum().reset_index()
    fig = px.pie(pie_df, names="Subcategory", values="Amount", title="Expenses by Subcategory")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📅 Monthly Trends")
    trend_df = filtered_df.groupby([df["Date"].dt.to_period("M"), "Category"])["Amount"].sum().reset_index()
    trend_df["Date"] = trend_df["Date"].astype(str)
    fig2 = px.bar(trend_df, x="Date", y="Amount", color="Category", barmode="group", title="Monthly Financial Trends")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available for selected filters.")


