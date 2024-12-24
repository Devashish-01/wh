import streamlit as st
from streamlit_option_menu import option_menu

# Load pages
from data_input import main as data_input_page
from repayment import main as repayment_page
from dashboard import main as dashboard_page


with st.sidebar:
    selected = option_menu(
        "Menu",
        ["Dashboard", "Liabilities", "Portfolio"],
        icons=["house", "list-task", "pie-chart"],
        menu_icon="cast",
        default_index=0
    )

# Render the selected page
if selected == "Dashboard":
    dashboard_page()
elif selected == "Liabilities":
    data_input_page()
elif selected == "Portfolio":
    repayment_page()
