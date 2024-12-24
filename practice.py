import streamlit as st
import pandas as pd
from utils import *
DATA_FILE = "liabilities.json"
liabilities = load_data(DATA_FILE)
import streamlit as st
import pandas as pd

# Function to render EMI sections in tabs
def render_emi_section_tab(title, emi_df, updated_emi_list):
    """
    Renders an EMI section within a tab with checkboxes for updating 'done' status.

    Args:
        title (str): Title of the section.
        emi_df (pd.DataFrame): DataFrame containing EMI details.
        updated_emi_list (list): List to collect updated EMI rows.
    """
    st.subheader(title)

    if emi_df.empty:
        st.info(f"No EMIs in the '{title}' category.")
    else:
        # Display scrollable data for large datasets
        st.dataframe(emi_df, height=400)

        # Display checkboxes for each row to mark 'done'
        st.write("**Mark EMIs as Paid:**")
        for index, row in emi_df.iterrows():
            new_done = st.checkbox(
                f"{row['lender_name']} | {row['date']} | ₹{row['amount']}",
                value=row["done"],
                key=f"{title}_{index}"
            )
            row["done"] = new_done
            updated_emi_list.append(row.to_dict())


# Load EMI data into DataFrames
upcoming_emi_list = pd.DataFrame(get_upcoming_emi(liabilities["liabilities"]))
completed_emi_list = pd.DataFrame(get_complete_emi(liabilities["liabilities"]))
emi_not_paid_ = pd.DataFrame(emi_not_paid(liabilities["liabilities"])[0])
emi_today_ = pd.DataFrame(emi_today(liabilities["liabilities"]))

# Dashboard title and description
st.title("📊 EMI Management Dashboard")
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
    render_emi_section_tab("Due Today", emi_today_, updated_emi_list)

with tab_upcoming:
    render_emi_section_tab("Upcoming EMIs", upcoming_emi_list, updated_emi_list)

with tab_overdue:
    render_emi_section_tab("Overdue EMIs", emi_not_paid_, updated_emi_list)

with tab_completed:
    render_emi_section_tab("Completed EMIs", completed_emi_list, updated_emi_list)

# Save changes button at the bottom
if st.button("💾 Save Changes"):
    updated_json = update_json_with_done(liabilities, updated_emi_list)
    save_data(updated_json, DATA_FILE)
    st.success("🎉 EMI statuses updated and saved to JSON!")
