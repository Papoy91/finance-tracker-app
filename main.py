import streamlit as st
from datetime import date

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from google.oauth2 import service_account

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
