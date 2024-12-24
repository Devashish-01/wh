import streamlit as st
import pandas as pd
from utils import *

DATA_FILE = "liabilities.json"

def main():
    st.title("📊 Dashboard")
    st.write("An overview of your financial liabilities and metrics.")

    # Load data
    liabilities = load_data(DATA_FILE)

    # Metrics
    total_liabilities = sum([lender["total_liabilities"] for lender in liabilities["liabilities"].values()])
    active_loans = sum([lender["active_no_of_loan"] for lender in liabilities["liabilities"].values()])
    upcoming_emis = sum([len(lender["emi_list"]) for lender in liabilities["liabilities"].values()])
    
    # Display Metrics
    st.metric("Total Liabilities", f"${total_liabilities:,.2f}")
    st.metric("Active Loans", active_loans)
    st.metric("Upcoming EMIs", upcoming_emis)

    upcoming_emi_list  = get_upcoming_emi(liabilities["liabilities"])
    completed_emi_list = get_complete_emi(liabilities["liabilities"])
    emi_not_paid_ = emi_not_paid(liabilities["liabilities"])
    emi_today_ = emi_today(liabilities["liabilities"])
    
    upcoming_emi_list = pd.DataFrame(upcoming_emi_list)
    completed_emi_list =  pd.DataFrame(completed_emi_list)
    emi_not_paid_ = pd.DataFrame(emi_not_paid_)
    emi_today_ = pd.DataFrame(emi_today_)

    # Dashboard title and description
    st.title("EMI Details")
    st.markdown(
        """
        Welcome to the EMI Management System! Use the tabs below to view and update EMI statuses:
        - **Due Today**: EMIs that are due today.
        - **Upcoming EMIs**: EMIs scheduled for future dates.
        - **Overdue EMIs**: EMIs that are overdue and not yet paid.
        - **Completed EMIs**: EMIs that have already been paid.
        """
    )

    # Tabs for different EMI categories
    tab_due_today, tab_upcoming, tab_overdue, tab_completed = st.tabs(
        ["📅 Due Today", "⏳ Upcoming EMIs", "⚠️ Overdue EMIs", "✅ Completed EMIs"]
    )

    updated_emi_list = []

    # Render EMI sections in tabs
    with tab_due_today:
        render_emi_section_tab("Due Today", emi_today_, updated_emi_list , "null", "null")

    with tab_upcoming:
        render_emi_section_tab("Upcoming EMIs", upcoming_emi_list, updated_emi_list , "null", "null")

    with tab_overdue:
        render_emi_section_tab("Overdue EMIs", emi_not_paid_, updated_emi_list , "null", "null")

    with tab_completed:
        render_emi_section_tab("Completed EMIs", completed_emi_list, updated_emi_list , "null", "null")

    # Save changes button at the bottom
    if st.button("🗂 Save Changes"):
        updated_json = update_json_with_done(liabilities, updated_emi_list)
        save_data(updated_json, DATA_FILE)
        st.success("🎉 EMI statuses updated and saved to JSON!")

    # Show liabilities summary
    st.header("Liabilities Overview")
    for lender_name, details in liabilities["liabilities"].items():
        st.subheader(lender_name)
        st.write(f"Total Liabilities: ${details['total_liabilities']:.2f}")
        st.write(f"Active Loans: {details['active_no_of_loan']}")
        st.write("Loans:")
        st.json(details["loans"])

if __name__ == "__main__":
    main()
