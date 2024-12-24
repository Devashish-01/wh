import streamlit as st
import os
from datetime import date, timedelta , datetime
from dateutil.relativedelta import relativedelta
import pandas as pd 


# Load Data    
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            st.warning("Data file is corrupted. Resetting to default structure.")
            return {"liabilities": {}}
    else:
        return {"liabilities": {}}
    
# Save Data
def save_data(data, file_path):
    """
    Save the liabilities data to a JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def security_check():
    st.write("Enter CONFIRM to complete the transaction")
    x = st.text_input("CONFIRM")
    if(x == "CONFIRM"):
        return True
    return False

            
# Give list of emi 
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def emi_list(start_date, deadline_months, interval_months, amount, lender_name, transaction_id):
    emis = []
    current_date = start_date + relativedelta(months=interval_months)
    end_date = start_date + relativedelta(months=deadline_months)
    count = int((end_date - start_date).days / (interval_months * 30))

    # Generate EMIs for the duration of the loan
    for i in range(count + 1):
        # Ensure `current_date` is a `datetime` object
        # if isinstance(current_date, datetime):
        #     formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
        # else:
        #     # Convert `current_date` to `datetime`
        #     formatted_date = datetime.combine(current_date, datetime.min.time()).strftime("%Y-%m-%d %H:%M:%S")
        formatted_date = str(current_date) + " " + str(datetime.now()) 

        emis.append({
            "date": formatted_date,
            "amount": amount,
            "done": False,
            "lender_name": lender_name,
            "id": transaction_id,
            "remark": []
        })
        # Move to the next EMI date
        current_date = current_date + relativedelta(months=interval_months)

    return emis



def interest_accumulated(emi_dates, interest_rate, current_principal): 
    sum = 0
    d2 = date.today()
    d1 = str(d2)
    for i in emi_dates:
        if date.fromisoformat(i["date"].split(" ")[0]) <= d2:
                sum += i["amount"]
                d1 = i["date"]
    d1 = date.fromisoformat(d1.split(" ")[0])

    print(f"Calculating interest accumulated from {d1} to {d2}")
    months = round(((d2.year - d1.year) + (d2.month - d1.month)/12.0 + (d2.day - d1.day) / 365.0)*12, 2)
    print(f"Months calculated: {months}")
    interest_amount = round((months * interest_rate * current_principal) / 100.0, 3)
    print(f"Interest amount calculated: {interest_amount}")
    return interest_amount, months

def change_emi_for_repayment (emi , next_emi_date , interest_made , interest_future , repayment_remark):
    current_date = date.today()
    for i in range(len(emi)) :
        if date.fromisoformat(emi[i]["date"]) == next_emi_date:
            emi[i]["amount"] = interest_future + interest_made
            emi[i]["remark"].append(f"""
            You had done one repayment on date: {date.today().strftime('%Y-%m-%d')}
            - **Interest added**: {interest_made : .2f}
            - **Repayment remark**: {repayment_remark}
            """)

        elif date.fromisoformat(emi[i]["date"].split(" ")[0]) > current_date:
            emi[i]["amount"] = interest_future
    return emi


def previous_emi_date(emi_list):
    current_date = date.today()  # Get today's date
    previous_date = current_date  # Initialize previous_date to today's date
    
    for emi in emi_list:
        emi_date = date.fromisoformat(emi["date"].split(" ")[0])  # Correct usage
        if emi_date > current_date:
            break
        previous_date = emi_date
    
    return previous_date  # Return the previous EMI date

#remove all emis having due_date > current_date
def remove_further_emi(loan):
    emi = loan["interest_payment_interval_months"]

    current_date = date.today()
    emi_updated = []
    for i in range(len(emi)):
        temp = date.fromisoformat(emi[i]["date"].split(" ")[0])
        if temp <=  current_date : 
            emi_updated.append(emi[i])
    
    return emi_updated

# Helper to find the next minimum available loan ID
def get_next_id(loans):
    existing_ids = [int(key) for key in loans.keys()] if loans else []
    return min(set(range(1, max(existing_ids, default=0) + 2)) - set(existing_ids))

# Extract Upcoming EMI List of speific lender
def upcoming_emi_list(liabilities):
    emi_list = []
    today = date.today()  # Current date

    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                emi_date = date.fromisoformat(emi["date"].split(" ")[0])
                # Check if EMI date is in the future and the EMI is not done
                if today < emi_date and not emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"].split(" ")[0]))
    return sorted_emi_list

# Extract Upcoming EMI List
def upcoming_emi_list(liabilities):
    emi_list = []
    today = date.today()  # Current date
    
    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                emi_date = date.fromisoformat(emi["date"].split(" ")[0])
                # Check if EMI date is in the future and the EMI is not done
                if today < emi_date and not emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"]))
    return sorted_emi_list


# Extract Upcoming EMI List
def get_upcoming_emi(liabilities):
    emi_list = []
    today = date.today()  # Current date
    
    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                emi_date = date.fromisoformat(emi["date"].split(" ")[0])
                # Check if EMI date is in the future and the EMI is not done
                if today < emi_date and not emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"].split(" ")[0]))
    return sorted_emi_list

def get_complete_emi(liabilities):
    emi_list = []
    today = date.today()  # Current date
    
    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                # Check if EMI date is in the future and the EMI is not done
                if emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"].split(" ")[0]))
    return sorted_emi_list

def emi_not_paid(liabilities):
    emi_list = []
    today = date.today()  # Current date
    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                emi_date = date.fromisoformat(emi["date"].split(" ")[0])
                # Check if EMI date is in the future and the EMI is not done
                if today > emi_date and not emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"].split(" ")[0]))
    return sorted_emi_list 

def emi_today(liabilities):
    emi_list = []
    today = date.today()  # Current date
    
    # Iterate through lenders
    for lender, lender_data in liabilities.items():
        # Iterate through loans
        for loan_id, loan_data in lender_data["loans"].items():
            # Iterate through the upcoming EMI list
            for emi in loan_data["upcoming_emi_list"]:
                emi_date = date.fromisoformat(emi["date"].split(" ")[0])
                # Check if EMI date is in the future and the EMI is not done
                if today == emi_date and not emi["done"]:
                    emi_list.append(emi)
    sorted_emi_list = sorted(emi_list, key=lambda x: date.fromisoformat(x["date"].split(" ")[0]))
    return sorted_emi_list



# Extract EMI data from JSON
def extract_emi_data(json_data):
    emi_list = []
    for lender, lender_data in json_data["liabilities"].items():
        for loan_id, loan_data in lender_data["loans"].items():
            for emi in loan_data["upcoming_emi_list"]:
                emi["lender_name"] = lender  # Add lender name for context
                emi["loan_id"] = loan_id    # Add loan ID for context
                emi_list.append(emi)
    return emi_list

def update_json_with_done(json_data, updated_emi_list):
    for emi in updated_emi_list:
        lender_name = emi["lender_name"]
        loan_id = str(emi["id"])  # Convert loan_id to string as JSON keys are strings
        date = emi["date"].split(" ")[0]
        
        # Navigate to the correct EMI entry
        if (
            lender_name in json_data["liabilities"] and
            loan_id in json_data["liabilities"][lender_name]["loans"]
        ):
            upcoming_emi_list = json_data["liabilities"][lender_name]["loans"][loan_id]["upcoming_emi_list"]
            
            # Update the 'done' status for matching EMIs
            for loan_emi in upcoming_emi_list:
                if loan_emi["date"].split(" ")[0] == date and loan_emi["id"] == loan_id:
                    loan_emi["done"] = emi["done"]
    
    return json_data

data_file = "liabilities.json"
liabilities_data = load_data(data_file)

def sum_of_paid_emis(emi_list):
    amount = 0
    for i in emi_list:
        if i["done"] == True:
            amount += i["amount"]
    return amount


def get_time(d1):
    d2 = date.today()
    return round(((d2.year - d1.year) + (d2.month - d1.month)/12.0 + (d2.day - d1.day) / 365.0)*12 , 2)

#def total_liabilities {
# - update ["interest_accumulated_till_today"]
# - update ["current_principal"]
# - update ["final_amount"]
# }
def total_liabilities(liabilities):
    total_liabilities = 0
    for lender , lender_data in liabilities.items():
        total_liabilities_lender = 0
        for loan_id, loan_data in lender_data["loans"].items():
            emi_list = loan_data["upcoming_emi_list"]
            interest_rate = loan_data["interest_rate"]
            current_principal = loan_data["current_principal"]
            total_liabilities += current_principal
            total_liabilities_lender += current_principal
            d2 = date.today()
            d1 = d2
            interest_amount = 0.00
            for i in emi_list:
                if  date.fromisoformat(i["date"].split(" ")[0]) <= d2:
                    if i["done"] == False:
                        interest_amount += i["amount"] 
                    d1 = date.fromisoformat(i["date"].split(" ")[0])

            d3 = date.fromisoformat(loan_data["transaction_date"])
            # month total from starting date to now 
            months = round(((d2.year - d3.year) + (d2.month - d3.month)/12.0 + (d2.day - d3.day) / 365.0)*12 , 2)

            # month from the previous emi date to now so to calculate interest incurred on the current principal 
            months1 = round(((d2.year - d1.year) + (d2.month - d1.month)/12.0 + (d2.day - d1.day) / 365.0)*12 , 2)

            interest_amount += round((months1 * interest_rate * current_principal)/100.0 , 3)
            loan_data["Interest_accumulated_till_today"] = interest_amount , months
            total_liabilities += interest_amount
            total_liabilities_lender += interest_amount
        lender_data["total_liabilities"] = total_liabilities_lender
    return total_liabilities

def render_emi_section_tab(title: str, emi_df: pd.DataFrame, updated_emi_list: list, ln: str, li: str) -> None:
    """
    Renders an EMI section within a tab with checkboxes for updating 'done' status.

    Args:
        title (str): Title of the section.
        emi_df (pd.DataFrame): DataFrame containing EMI details.
        updated_emi_list (list): List to collect updated EMI rows.
        ln (str): Lender name.
        li (str): Loan ID.

    Returns:
        None
    """

    st.subheader(title)

    if emi_df.empty:
        st.info(f"No EMIs in the '{title}' category.")
        return

    st.write("**Mark EMIs as Paid:**")

    for index, row in emi_df.iterrows():
        checkbox_key = f"{title}_{row['lender_name']}_{row['id']}_{index}"  # Unique key for each checkbox
        if ln == row["lender_name"] and li == str(row["id"]):
            new_done = st.checkbox(
                f"{row['lender_name']} | {row['date']} | ₹{row['amount']}",
                value=row["done"],
                key=checkbox_key
            )
            row["done"] = new_done
            updated_emi_list.append(row.to_dict())
        elif ln == "null" and li == "null":
            new_done = st.checkbox(
                f"{row['lender_name']} | {row['date']} | ₹{row['amount']}",
                value=row["done"],
                key=checkbox_key
            )
            row["done"] = new_done
            updated_emi_list.append(row.to_dict())
        else:
                continue
        

    # Save changes button at the bottom
    DATA_FILE = "liabilities.json"
    liabilities = load_data(DATA_FILE)
    save_button_key = f"{title}_{ln}_{li}_save"  # Unique key for the save button
    if ln != "null" and li != "null" and ln in row["lender_name"] and li in str(row["id"]):
        if st.button(f"🗂 Save Changes of {ln} and {li}", key=save_button_key):
            updated_json = update_json_with_done(liabilities, updated_emi_list)
            save_data(updated_json, DATA_FILE)
            st.success("🎉 EMI statuses updated and saved to JSON!")
    else:
        if st.button(f"🗂 Save Changes of {title}", key=f"{title}_save"):
            updated_json = update_json_with_done(liabilities, updated_emi_list)
            save_data(updated_json, DATA_FILE)
            st.success("🎉 EMI statuses updated and saved to JSON!")



def refresh():
    #refresh every total_liabilities
    total_liabilities = total_liabilities(liabilities_data["liabilities"])
    #refresh all the interest_accumulated_till_today 
    




from datetime import date


