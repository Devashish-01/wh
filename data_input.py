import streamlit as st
import json
from utils import *
from datetime import date
import os

# -------------------- App Configuration -------------------- #
st.set_page_config(
    page_title="Liability Management",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)

# -------------------- Constants -------------------- #
DATA_FILE = "liabilities.json"
REFRESH_INTERVAL = 1  # Time in seconds for refreshing data

# -------------------- Data Handling -------------------- #
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data(file_path):
    """Load data from a JSON file with error handling."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            st.warning("Data file was empty or corrupted. Resetting to default structure.")
            return {"liabilities": {}}
    else:
        st.warning("Data file not found. Creating a new one.")
        return {"liabilities": {}}

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# -------------------- UI Components -------------------- #
def add_liability_form(liabilities_data):
    """Form to add a new liability or loan."""
    with st.expander("Add Liability"):
        name = st.text_input("Name", placeholder="Enter liability name").lower()
        principal = st.number_input("Principal", min_value=0.0, step=1.0)
        interest_rate = st.number_input("Interest Rate per month (%)", step=1.0, format="%.2f")
        deadline_months = st.number_input("Deadline (Months)", min_value=0.0, step=1.0)
        interval = st.number_input("Interest payment interval (months)", step=1.0, format="%.2f")
        active = st.checkbox("Active", value=True)
        transaction_date = st.date_input("Transaction Date (year - month - date)")
        remark = st.text_input("Remark", placeholder="Add any remarks")

        if st.button("Add Loan"):
            process_new_loan(
                name, principal, interest_rate, deadline_months, interval, active, transaction_date, remark, liabilities_data
            )

def process_new_loan(name, principal, interest_rate, deadline_months, interval, active, transaction_date, remark, liabilities_data):
    """Handles the addition of a new loan and updates the data."""
    if not name:
        st.error("Name is required to add a loan.")
        return
    if not principal:
        st.error("Principal is required to add a loan.")
        return

    if name not in liabilities_data["liabilities"]:
        liabilities_data["liabilities"][name] = {
            "active": True,
            "active_no_of_loan": 0,
            "loans": {},
            "total_liabilities": 0,
            "emi_list": {},
        }

    liability = liabilities_data["liabilities"][name]
    next_id = get_next_id(liability["loans"])
    interest_amount = round((principal * interest_rate * interval) / 100.0, 3)
    emi_list_ = emi_list(transaction_date, deadline_months, interval, interest_amount, name, next_id)
    registration_time_ = datetime.min.now()

    liability["loans"][next_id] = {
        "active": active,
        "transaction_date": str(transaction_date),
        "registration_time" : str(registration_time_),
        "date_of_data_entry": str(date.today()),
        "main_principal": principal,
        "current_principal": principal,
        "interest_rate": interest_rate,
        "interest_payment_interval_months": interval,
        "deadline_months": deadline_months,
        "remark": remark,
        "upcoming_emi_list": emi_list_,
        "repayment_list": {},
    }
    interest_accumulated_ = interest_accumulated(emi_list_ , interest_rate, principal)

    liability["loans"][next_id]["Interest_accumulated_till_today"] = interest_accumulated_[0]
    liability["loans"][next_id]["final_amount"] = interest_accumulated_[0] + principal
    liability["loans"][next_id]["upcoming_emi_list"] = interest_accumulated_[0] + principal

    liability["active_no_of_loan"] += 1
    liability["total_liabilities"] = total_liabilities(liabilities_data["liabilities"])

    save_data(DATA_FILE, liabilities_data)
    st.success(f"Loan added successfully to '{name}' with ID {next_id}!")


def show_data(liabilities_data):
    """Displays the current liabilities in a readable format."""
    st.header("Current Liabilities")

    if liabilities_data["liabilities"]:
        for liability_name, details in liabilities_data["liabilities"].items():
            st.subheader(f"Name: {liability_name}")
            st.write(f"Active: {details['active']}")
            st.write(f"Number of Active Loans: {details['active_no_of_loan']}")
            st.write(f"Total Liabilities: {details['total_liabilities']}")
            st.write("Loans:")
            if details["loans"]:
                for loan_id, loan_details in details["loans"].items():
                    st.write(f"- **Loan ID {loan_id}:**")
                    st.json(loan_details)
            else:
                st.write("No loans added yet.")
    else:
        st.write("No liabilities found.")

# -------------------- Main App -------------------- #
def main():
    st.title("Liabilities Management")
    st.write("Add new liabilities or manage existing ones.")

    liabilities_data = load_data(DATA_FILE)

    add_liability_form(liabilities_data)
    show_data(liabilities_data)
    save_data(DATA_FILE, liabilities_data)

# -------------------- Run the App with Auto-Refresh -------------------- #
if __name__ == "__main__":
    main()
