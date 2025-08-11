import streamlit as st
from datetime import date
from utils.gsheet import connect_sheet

st.title("📋 Add New Financial Entry")

section = st.sidebar.selectbox("Select Section", ["USA", "India"])
category = st.selectbox("Select Category", ["Earning", "Expense", "Invest", "Transfer"])

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

subcategory_list = subcategory_options.get(section, {}).get(category, [])
if not subcategory_list:
    st.warning("This category is not available in the selected section.")
else:
    subcategory = st.selectbox("Select Subcategory", subcategory_list)
    note = st.text_input("Enter custom note") if subcategory == "Other" else ""
    amount = st.number_input("Enter Amount", min_value=0.0, format="%.2f")
    entry_date = st.date_input("Date", value=date.today())
    currency = "$" if section == "USA" else "₹"

    if st.button("Submit Entry"):
        sheet = connect_sheet()
        row = [str(entry_date), section, category, subcategory, note, amount]
        sheet.append_row(row)
        st.success("✅ Entry saved to Google Sheet!")
        st.success(f"Saved: {section} - {category} - {subcategory} - {note} - {currency}{amount} on {entry_date}")
