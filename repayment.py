import streamlit as st
from utils import *
import pandas as pd
from datetime import date , datetime 

# Set page config as the first Streamlit command
# st.set_page_config(page_title="Portfolio Management", layout="wide")

DATA_FILE = "liabilities.json"

def delete_lender(liabilities, lender_name):
    """Delete an entire lender from the liabilities"""
    if lender_name in liabilities["liabilities"]:
        del liabilities["liabilities"][lender_name]
        save_data(liabilities, DATA_FILE)
        st.success(f"Lender {lender_name} has been completely removed.")
        return True
    return False

def delete_loan(liabilities, lender_name, loan_id):
    """Delete a specific loan from a lender"""
    if lender_name in liabilities["liabilities"]:
        lender = liabilities["liabilities"][lender_name]
        if loan_id in lender["loans"]:
            # Reduce total liabilities and active loan count
            lender["total_liabilities"] -= lender["loans"][loan_id]["main_principal"]
            lender["active_no_of_loan"] -= 1
            
            # Remove the loan
            del lender["loans"][loan_id]
            
            # Save changes
            save_data(liabilities, DATA_FILE)
            st.success(f"Loan {loan_id} for {lender_name} has been deleted.")
            return True
    return False

def main():
    st.title("Portfolio Management")
    st.write("View lender portfolios, manage repayments, and track liabilities.")

    # Load liabilities
    liabilities = load_data(DATA_FILE)

    # Check if there are any lenders
    if not liabilities["liabilities"]:
        st.warning("No lenders found. Please add a lender first.")
        return

    # Lender Selection
    lender_names = list(liabilities["liabilities"].keys())
    lender_name = st.selectbox("Select Lender", lender_names)

    if lender_name:
        lender = liabilities["liabilities"][lender_name]
        
        # Lender Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Liabilities", f"₹{lender['total_liabilities']:,.2f}")
        with col2:
            st.metric("Active Loans", lender['active_no_of_loan'])
        with col3:
            st.metric("Lender Status", "Active" if lender['active'] else "Inactive")

        # Loan Management Section
        st.subheader("Loan Details")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Loan Overview", "Loan Actions"])
        
        with tab1:
            # Loan Overview
            for loan_id, loan in lender["loans"].items():
                with st.expander(f"Loan {loan_id} Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Principal:** ₹{loan['main_principal']:,.2f}")
                        st.write(f"**Current Principal:** ₹{loan['current_principal']:,.2f}")
                        st.write(f"**Interest Rate:** {loan['interest_rate']}%")
                    with col2:
                        st.write(f"**Transaction Date:** {loan['transaction_date']}")
                        st.write(f"**Deadline:** {loan['deadline_months']} months")
                        st.write(f"**Status:** {'Active' if loan['active'] else 'Inactive'}")
                    with col3:
                        st.write(f"**Transaction Date:** {loan['transaction_date']}")
                        st.write(f"**Deadline:** {loan['deadline_months']} months")
                        st.write(f"**Status:** {'Active' if loan['active'] else 'Inactive'}")
                    
                    # EMI Schedule
                    st.subheader("Upcoming EMI Schedule")
                    
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
                        render_emi_section_tab("Due Today", emi_today_, updated_emi_list , lender_name , loan_id)

                    with tab_upcoming:
                        render_emi_section_tab("Upcoming EMIs", upcoming_emi_list, updated_emi_list , lender_name , loan_id)

                    with tab_overdue:
                        render_emi_section_tab("Overdue EMIs", emi_not_paid_, updated_emi_list , lender_name , loan_id)

                    with tab_completed:
                        render_emi_section_tab("Completed EMIs", completed_emi_list, updated_emi_list , lender_name , loan_id)

                    

        with tab2:
            # Loan Actions
            st.subheader("Loan Management")
            
            # Repayment Form
            with st.form("repayment_form"):
                st.write("Loan Repayment")
                loan_id = st.selectbox("Select Loan", list(lender["loans"].keys()))
                amount = st.number_input("Repayment Amount", min_value=0.0)
                remark = st.text_input("Remark (optional)")
                confirm = st.form_submit_button("Submit Repayment")

                if confirm:
                    loan = lender["loans"][loan_id]
                    final_loan = loan["final_amount"]
                    #update loan["final_amount"] in all places
                    if amount == final_loan:
                        loan["loan_clear_amount"] = sum_of_paid_emis(loan["upcoming_emi_list"]) + final_loan
                        loan["current_principal"] = 0
                        loan["final_amount"] = 0
                        loan["interest_payment_interval_months"] = remove_further_emi(loan),
                        loan["active"] = False,
                        loan["deadline_months"] = get_time(loan["transcation_date"])

                    elif amount > loan["current_principal"]:
                        st.error("Repayment amount exceeds remaining balance.")
                    else:
                        loan["current_principal"] -= amount
                        
                        # Add to repayment list
                        if "repayment_list" not in loan:
                            loan["repayment_list"] = {}
                        
                        repayment_id = len(loan["repayment_list"]) + 1
                        loan["repayment_list"][str(repayment_id)] = {
                            "date": str(date.today()),
                            "amount": amount,
                            "remark": remark
                        }

                        # interest_amount = (principal * (interest_rate*interest_payment_interval))/100
                        # emi = loan["upcomin_emi_list"]
                        # next_emi_date = 
                        # emi_list_ = change_emi_for_repayment (emi , next_emi_date , interest_made , interest_future , repayment_remark)
                        
                        # #interest accumulated till now ,paid emi excluded
                        # interest_accumulated_ = interest_accumulated(emi_list_ ,   transaction_date   ,interest_rate , principal)

                        # loan["interest_accumulated_till_today"] = interest_accumulated()

                        # Save changes
                        save_data(liabilities, DATA_FILE)
                        st.success("Repayment successful!")

            # Deletion Actions
            st.subheader("Danger Zone")
            col1, col2 = st.columns(2)
            
            with col1:
                # Delete Loan
                st.write("**Delete Specific Loan**")
                loan_to_delete = st.selectbox("Select Loan to Delete", list(lender["loans"].keys()))
                if st.button("Delete Selected Loan", type="primary"):
                    delete_loan(liabilities, lender_name, loan_to_delete)
                    st.experimental_rerun()

            with col2:
                # Delete Entire Lender
                st.write("**Delete Entire Lender**")
                if st.button("Delete Lender", type="primary"):
                    delete_lender(liabilities, lender_name)
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
