from flask import Blueprint, render_template, request, jsonify
from app.models import Utility, Expense, Gas
from app import db
from datetime import datetime

bp = Blueprint('routes', __name__)      # Creating a blueprint named routes

def get_expense_data(selected_month):
    """
    Helper function to get expense data for a given month.

    Returns:
    3 lists containing the dates, expense values, and the breakdown of each item.
    """

    # Extracts/Orders the data whose month is equal to the selected month
    expense_data = Expense.query.filter(db.extract('month', Expense.date) == selected_month).order_by(Expense.date).all() 

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

@bp.route('/')
def home():
    """
    Extracts information from each database and creates lists which are used to create different graphs in home.html.

    Returns:
    A rendered home page with different graphs using the different lists from each database analysing spending from each of the routes.
    """
    selected_month = int(request.args.get('month', datetime.now().month))       # Int of the selected month which is used to handle the functionality of the month selector on the graphs

    # # Expense Database
    # expense_data = Expense.query.filter(db.extract('month', Expense.date) == selected_month).order_by(Expense.date).all()   # Extracts/Orders the data whose month is equal to the selected month

    # # Making arrays of dates prices and description
    # expense_dates = [expense.date.strftime('%m/%d') for expense in expense_data]
    # expense_values = [expense.price for expense in expense_data]
    # expense_descriptions = [expense.description for expense in expense_data]

    # # Combines the expenses with the same date
    # # If there is an entry for that date, add to existing total and item description else make a new entry
    # # Use the date as the key and the price/description as its values
    # expense_dict = {}
    # for date, price, description in zip(expense_dates, expense_values, expense_descriptions):       # Zip the lists together to form tuples in the format (date, price, description)
    #     if date in expense_dict:
    #         expense_dict[date]['total'] += price
    #         expense_dict[date]['items'].append(f"{description}: ${price:.2f}")      
    #     else:
    #         expense_dict[date] = {'total': price, 'items': [f"{description}: ${price:.2f}"]}     

    # # Separate the formatted data from the dictionary into lists for chart creation
    # expense_date_labels = list(expense_dict.keys())
    # expense_total_values = [value['total'] for value in expense_dict.values()]
    # expense_breakdown = [value['items'] for value in expense_dict.values()]     # For the tooltip message to display what made up the total cost


    expense_date_labels, expense_total_values, expense_breakdown =  get_expense_data(selected_month)

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Utility Database

    utility_data = Utility.query.filter(db.extract('month', Utility.electric_start_date) == int(selected_month)).all()          # Extracting all entries of the selected month

    # Converts the strings to floats and sums it up
    # Workaround: Usually each entry is just 1 number but to not pass it as an array we use the sum() to make it into a number 
    electric = sum([float(utility.electric) for utility in utility_data])
    water = sum([float(utility.water) for utility in utility_data])
    internet = sum([float(utility.internet) for utility in utility_data])

    # Lists for chart creation
    pie_chart_labels = ['Water', 'Internet', 'Electric']
    pie_chart_values = [water, internet, electric]

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Gas Database

    # db.extract('month', Gas.date) extracts the month from gas.date and labels those entries with month
    # db.func.sum(Gas.price) sums up all the gas prices from that month and labels it total spending
    # group_by(db.extract('month', Gas.date)).all() allows me to retrieve all the entries with the same month together 
    gas_data = db.session.query(db.extract('month', Gas.date).label('month'), db.func.sum(Gas.price).label('total_spending')).group_by(db.extract('month', Gas.date)).all()

    # Lists for chart creation
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months = [int(record.month) for record in gas_data]     # List of months from the database as ints 
    gas_month_labels = [month_names[month-1] for month in months]   # List of the months that are in the database as strings 
    gas_total_spending = [record.total_spending for record in gas_data]    

    return render_template(
        'home.html',
        selected_month=selected_month,
        month_names=month_names, 
        gas_month_labels=gas_month_labels, 
        gas_total_spending=gas_total_spending, 
        pie_chart_values=pie_chart_values,
        pie_chart_labels=pie_chart_labels,
        expense_date_labels=expense_date_labels,
        expense_total_values=expense_total_values,
        expense_breakdown = expense_breakdown
    )

    # return jsonify(
    #     selected_month=selected_month,
    #     month_names=month_names, 
    #     gas_month_labels=gas_month_labels, 
    #     gas_total_spending=gas_total_spending, 
    #     pie_chart_values=pie_chart_values,
    #     pie_chart_labels=pie_chart_labels,
    #     expense_date_labels=expense_date_labels,
    #     expense_total_values=expense_total_values,
    #     expense_breakdown = expense_breakdown
    # )



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
    expense_date_labels, expense_total_values, expense_breakdown =  get_expense_data(selected_month)
    return jsonify({
        'expense_date_labels': expense_date_labels,
        'expense_total_values': expense_total_values, 
        'expense_breakdown': expense_breakdown
    })
