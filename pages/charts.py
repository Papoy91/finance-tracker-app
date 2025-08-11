import streamlit as st
from utils.gsheet import load_data
import plotly.express as px

st.title("📊 Financial Summary & Charts")

df = load_data()

with st.expander("🔍 Filter Data"):
    selected_section = st.multiselect("Section", options=df["Section"].unique(), default=list(df["Section"].unique()))
    selected_category = st.multiselect("Category", options=df["Category"].unique(), default=list(df["Category"].unique()))
    date_range = st.date_input("Date Range", value=[df["Date"].min(), df["Date"].max()])

filtered_df = df[
    (df["Section"].isin(selected_section)) &
    (df["Category"].isin(selected_category)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

total_earning = filtered_df[filtered_df["Category"] == "Earning"]["Amount"].sum()
total_expense = filtered_df[filtered_df["Category"] == "Expense"]["Amount"].sum()
total_transfer = filtered_df[filtered_df["Category"] == "Transfer"]["Amount"].sum()
net_balance = total_earning - total_expense

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Earning", f"${total_earning:,.2f}")
col2.metric("💸 Total Expense", f"${total_expense:,.2f}")
col3.metric("🔁 Total Transfer", f"${total_transfer:,.2f}")
col4.metric("📉 Net Balance", f"${net_balance:,.2f}")

if not filtered_df.empty:
    st.subheader("📊 Expense Breakdown")
    pie_df = filtered_df[filtered_df["Category"] == "Expense"].groupby("Subcategory")["Amount"].sum().reset_index()
    fig = px.pie(pie_df, names="Subcategory", values="Amount", title="Expenses by Subcategory")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📅 Monthly Trends")
    trend_df = filtered_df.groupby([filtered_df["Date"].dt.to_period("M"), "Category"])["Amount"].sum().reset_index()
    trend_df["Date"] = trend_df["Date"].astype(str)
    fig2 = px.bar(trend_df, x="Date", y="Amount", color="Category", barmode="group", title="Monthly Financial Trends")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available for selected filters.")