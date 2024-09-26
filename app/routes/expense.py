from flask import Blueprint, render_template, request, jsonify
from app.models import Expense
from app import db
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

def get_expense_data(selected_month, current_year):
    """
    Helper function to get expense data for a given month.

    Returns:
    3 lists containing the dates, expense values, and the breakdown of each item.
    """
    # Extracts and orders data whose month is equal to the selected month and current year
    expense_data = Expense.query.filter(db.extract('month', Expense.date) == selected_month, db.extract('year', Expense.date) == current_year).order_by(Expense.date).all()   

    # Making arrays of dates prices and description
    expense_dates = [expense.date.strftime('%m/%d') for expense in expense_data]
    expense_values = [expense.price for expense in expense_data]
    expense_descriptions = [expense.description for expense in expense_data]

    # Combines the expenses with the same date
    # If there is an entry for that date, add to existing total and item description else make a new entry
    # Use the date as the key and the price/description as its values
    expense_dict = {}
    for date, price, description in zip(expense_dates, expense_values, expense_descriptions):       # Zip the lists together to form tuples in the format (date, price, description)
        if date in expense_dict:
            expense_dict[date]['total'] += price
            expense_dict[date]['items'].append(f"{description}: ${price:.2f}")      
        else:
            expense_dict[date] = {'total': price, 'items': [f"{description}: ${price:.2f}"]}     

    # Separate the formatted data from the dictionary into lists for chart creation
    expense_date_labels = list(expense_dict.keys())
    expense_total_values = [value['total'] for value in expense_dict.values()]
    expense_breakdown = [value['items'] for value in expense_dict.values()]

    return expense_date_labels, expense_total_values, expense_breakdown

@expenses_bp.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    """
    Extracts data from the expense form to create a new object in the Expense database and to render expense.html with that information.

    Returns:
    A rendered expense page with information about the expenses.
    """
    if request.method == "POST":        # When the user submits entries make string lists of each part of the form
        descriptionList = request.form.getlist('description')
        priceList = request.form.getlist('price')
        dateList = request.form.getlist('date')
        cardList = request.form.getlist('card')

        # Loops through priceList and sums up the costs and creates a new Expense object for the Expense database
        total_spending = 0
        for i in range(len(priceList)):
            if priceList[i]:
                total_spending += float(priceList[i])
                date_object = datetime.strptime(dateList[i], '%Y-%m-%d').date()     # Converts date string into datetime object

                new_expense = Expense(
                    description=descriptionList[i],
                    price=float(priceList[i]),
                    card_used=cardList[i],
                    date=date_object
                )

                db.session.add(new_expense)
        db.session.commit()
        return render_template('expense.html', total_spending=total_spending)   
    
    return render_template('expense.html', total_spending=0)        # Renders with initial values of 0

@expenses_bp.route('/redraw_expense_chart', methods=['GET'])
def redraw_expense_chart():
    """
    Returns the expense data for the selected month in JSON format for the AJAX request whenever the right/left arrows are pressed
    """
    selected_month = int(request.args.get('month', datetime.now().month))
    current_year = datetime.now().year
    expense_date_labels, expense_total_values, expense_breakdown =  get_expense_data(selected_month, current_year)
    return jsonify({
        'expense_date_labels': expense_date_labels,
        'expense_total_values': expense_total_values, 
        'expense_breakdown': expense_breakdown
    })