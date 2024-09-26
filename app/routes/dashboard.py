from flask import Blueprint, render_template, request
from datetime import datetime
from app.routes.utility import get_utility_data
from app.routes.expense import get_expense_data
from app.routes.gas import get_gas_data  # Import from appropriate module

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """
    Calls each database helper function and returns the lists of information used to render home.html
    """
    # Expense and Utility will have their own separate select_month because before they were sharing the same month but when clicking on the forms it was indexing wrong into month_names
    # and causing it to display the incorrect month 
    expense_selected_month = int(request.args.get('expense_month', datetime.now().month))      
    utility_selected_month = int(request.args.get('utility_month', datetime.now().month))      

    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    current_month = datetime.now().month
    year_to_date_month_list = month_list[:current_month]
    current_year = datetime.now().year

    # Calling helper functions of each database to get the lists to render home.html 
    expense_date_labels, expense_total_values, expense_breakdown = get_expense_data(expense_selected_month, current_year)
    utility_labels, utility_values = get_utility_data(utility_selected_month, current_year)
    gas_total_spending = get_gas_data(current_year)

    return render_template(
        'home.html',
        year_to_date_month_list=year_to_date_month_list, 
        gas_total_spending=gas_total_spending, 
        utility_values=utility_values,
        utility_labels=utility_labels,
        utility_selected_month=utility_selected_month,
        expense_date_labels=expense_date_labels,
        expense_total_values=expense_total_values,
        expense_breakdown=expense_breakdown,
        expense_selected_month=expense_selected_month
    )