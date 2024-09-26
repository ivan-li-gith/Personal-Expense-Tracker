from flask import Blueprint, render_template, request, jsonify
from app.models import Utility, Expense, Gas
from app import db
from datetime import datetime
import requests

bp = Blueprint('routes', __name__)      # Creating a blueprint named routes

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

def get_utility_data(selected_month, current_year):
    # Extracting all entries of the selected month and from this year
    utility_data = Utility.query.filter(db.extract('month', Utility.electric_start_date) == int(selected_month), db.extract('year', Utility.electric_start_date) == current_year).all()          

    # Converts the strings to floats and sums it up
    # Workaround: Usually each entry is just 1 number but to not pass it as an array we use the sum() to make it into a number 
    electric = sum([float(utility.electric) for utility in utility_data])
    water = sum([float(utility.water) for utility in utility_data])
    internet = sum([float(utility.internet) for utility in utility_data])

    # Lists for chart creation
    utility_labels = ['Water', 'Internet', 'Electric']
    utility_values = [water, internet, electric]

    return utility_labels, utility_values

def get_gas_data(current_year):
    gas_data = Gas.query.filter(db.extract('year', Gas.date) == current_year).all()     # Filter entries by this year
    total_spending_dict = {}

    # Loop through the data and sum up all gas entries for each month
    for gas in gas_data:
        month = int(gas.date.strftime('%m'))
        if month in total_spending_dict:
            total_spending_dict[month] += float(gas.price)
        else:
            total_spending_dict[month] = float(gas.price)

    # This is to ensure that the value is matched up to the correct month. If we had used list() it reordered the values and didnt associate it to the right month
    gas_total_spending = [total_spending_dict.get(month, 0.0) for month in range(1,13)] 
    return gas_total_spending   

def fetch_stock_data(stock_symbol):
    api_key = 'CFW0GZBCVRUJ7Y4G'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=1min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    time = data['Time Series (1min)']
    latest_timestamp = list(time.keys())[0]


    current_price = time[latest_timestamp]['4. close']
    return {'symbol': stock_symbol, 'price': current_price, 'timestamp': latest_timestamp}





@bp.route('/')
def home():
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

@bp.route('/utilities', methods=['GET', 'POST'])
def add_utilities():
    """
    Extracts data from the utility form to create a new object in the Utility database and to render utility.html with that information.

    Returns:
    A rendered utility page with information about the utility costs and what each roommate owes.
    """
    utilities = Utility.query.all()     # Accessing all entries of the database

    if request.method == 'POST':        # When user submits a form grab the data from each of the fields
        electric = float(request.form.get('electric'))
        water = float(request.form.get('water'))
        internet = float(request.form.get('internet'))
        household_items = request.form.get('household_items')

        if household_items == '' or household_items is None:        # If the field is empty set the value to 0 else convert to float
            household_items = 0.0
        else:
            household_items = float(household_items)

        # Grabbing the date string for each billing period to convert into a datetime object and extracting just the date in form of YY/MM/DD
        electric_start_date = datetime.strptime(request.form.get('electric_start_date'), '%Y-%m-%d').date()
        electric_end_date = datetime.strptime(request.form.get('electric_end_date'), '%Y-%m-%d').date()
        water_start_date = datetime.strptime(request.form.get('water_start_date'), '%Y-%m-%d').date()
        water_end_date = datetime.strptime(request.form.get('water_end_date'), '%Y-%m-%d').date()
        internet_start_date = datetime.strptime(request.form.get('internet_start_date'), '%Y-%m-%d').date()
        internet_end_date = datetime.strptime(request.form.get('internet_end_date'), '%Y-%m-%d').date()

        utility_split = round((electric + water + internet + household_items)/5, 2)     # Splits the total cost between 5 people and rounds it to 2 decimals

        summary = {     # Dictionary containing all the information needed for the summary part of utility.html
            'electric': electric,
            'water': water,
            'internet': internet,
            'household_items': household_items,
            'total_cost': (electric + water + internet + household_items),
            'ava_owes': utility_split,
            'jess_owes': utility_split,
            'annica_owes': utility_split,
            'april_owes': utility_split
        }

        # Creates a new Utility object and saves it to the database
        new_utility = Utility(
            electric=electric, 
            water=water, 
            internet=internet, 
            household_item=household_items,
            electric_start_date=electric_start_date,
            electric_end_date=electric_end_date,
            water_start_date=water_start_date,
            water_end_date=water_end_date,
            internet_start_date=internet_start_date,
            internet_end_date=internet_end_date
        )

        db.session.add(new_utility)
        db.session.commit()
        utilities = Utility.query.all()     
        return render_template('utility.html', utilities=utilities, summary=summary)        # Renders utility.html with the processed information
    
    return render_template('utility.html', utilities=utilities)     # Renders a blank page if no form is submitted

@bp.route('/add_expense', methods=['GET','POST'])
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

@bp.route('/add_gas', methods=['GET','POST'])
def add_gas():
    """
    Extracts data from the gas form to create a new object in the Gas database and to render gas.html with that information.

    Returns:
    A rendered gas page with information about the gas costs and what the split is.
    """
    if request.method == "POST":        # When the user submits entries make string lists of each part of the form
        stationList = request.form.getlist('station')
        priceList = request.form.getlist('price')
        dateList = request.form.getlist('date')
        cardList = request.form.getlist('card')

        # Loops through priceList and sums up all the costs and creates a new Gas object and adds it into the Gas database
        total_price = 0
        for i in range(len(priceList)):
            if priceList[i]:
                total_price += float(priceList[i])
                date_object = datetime.strptime(dateList[i], '%Y-%m-%d').date()

                new_gas = Gas(
                    station=stationList[i],
                    price=priceList[i],
                    card_used=cardList[i],
                    date=date_object
                )

                db.session.add(new_gas)

        db.session.commit()
        split_price = round(total_price / 2, 2)     # Splits up the total cost between 2 people 
        return render_template('gas.html', split_price=split_price, total_price=total_price)
    
    return render_template('gas.html', split_price=0, total_price=0)        # Render the page with initial values of 0

@bp.route('/redraw_expense_chart', methods=['GET'])
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

@bp.route('/redraw_utility_chart', methods=['GET'])
def redraw_utility_chart():
    """
    Returns the utility data for the selected month in JSON format for the AJAX request whenever the right/left arrows are pressed
    """
    selected_month = int(request.args.get('month', datetime.now().month))
    current_year = datetime.now().year
    utility_labels, utility_values = get_utility_data(selected_month, current_year)
    return jsonify({
        'utility_labels': utility_labels,
        'utility_values': utility_values
    })

@bp.route('/stock_tracker', methods=['GET', 'POST'])
def stock_tracker():
    if request.method == 'POST':
        stock_symbol = request.form.get('symbol')
        num_shares = request.form.get('shares')
        stock_data = fetch_stock_data(stock_symbol)

        return render_template('stock_tracker.html', stock=stock_data, shares=num_shares)
    return render_template('stock_tracker.html')

@bp.route('/print_expense_entries')
def print_entries():
    # Query all entries in the Gas table
    expense_entries = Expense.query.all()

    # Create a list of dictionaries to represent each gas entry
    expense_entries_list = [
        {
            "id": entry.id,
            "station": entry.description,
            "price": entry.price,
            "date": entry.date.strftime('%Y-%m-%d'),  # Format the date
            "card_used": entry.card_used
        }
        for entry in expense_entries
    ]

    # Return the list as a JSON response
    return jsonify(expense_entries_list)
