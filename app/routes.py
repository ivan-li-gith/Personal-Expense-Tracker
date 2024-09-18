from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Utility, Expense, Gas
from app import db
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates

#creating a blueprint named routes
bp = Blueprint('routes', __name__)

@bp.route('/')
def home():

    # Collecting data from each database

    # # Utility database
    # utility_data = Utility.query.all()
    # electric = [utility.electric for utility in utility_data]


    current_month = datetime.now().month
    selected_month = request.form.get('month', current_month)

    # Expense database
    expense_data = Expense.query.filter(db.extract('month', Expense.date) == int(selected_month)).all()
    expense_prices = [expense.price for expense in expense_data]
    expense_dates = [expense.date for expense in expense_data]


    # reason why we zip and sort together is to ensure that the price is associated with the correct date
    # if we just sorted the lists as is the price would not match with the correct date
    sorted_expenses = sorted(zip(expense_dates, expense_prices), key=lambda x: x[0])  # Sort by date
    expense_dates, expense_prices = zip(*sorted_expenses)  # Unzip sorted data

    # Plotting expense data

    # creates a figure and axis
    fig, ax = plt.subplots()
    # dates = x axis and price = y axis. marker linestyle and color is just to represent what the plots would look like 
    # ax.scatter(expense_dates, expense_prices, color='g')
    ax.plot(expense_dates, expense_prices, marker='o', linestyle='-', color='g')

    # Format dates to avoid overlap, rotate them and display as 'MMM dd'
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # E.g., 'Sep 01'
    ax.xaxis.set_major_locator(mdates.DayLocator())  # Show every day
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels to make them readable

    ax.set_title(f'Expenses for {datetime.now().strftime("%B")} (up to today)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    # creates a binary stream of the data and then saves that binary stream into png form
    expense_img = io.BytesIO()
    plt.savefig(expense_img, format='png')
    expense_img.seek(0)
    # converts binary data into a string 
    expense_plot_url = base64.b64encode(expense_img.getvalue()).decode()
    plt.close

    return render_template('home.html', expense_plot_url=expense_plot_url, selected_month=selected_month)

@bp.route('/utilities', methods=['GET', 'POST'])
def add_utilities():

    #accessing all entries of the database
    utilities = Utility.query.all()

    #when the user submits a form grab that data
    if request.method == 'POST':
        electric = float(request.form.get('electric'))
        water = float(request.form.get('water'))
        internet = float(request.form.get('internet'))
        household_items = request.form.get('household_items')

        #handling when the field is empty
        if household_items == '' or household_items is None:
            household_items = 0.0
        else:
            household_items = float(household_items)

        electric_start_date = datetime.strptime(request.form.get('electric_start_date'), '%Y-%m-%d').date()
        electric_end_date = datetime.strptime(request.form.get('electric_end_date'), '%Y-%m-%d').date()

        water_start_date = datetime.strptime(request.form.get('water_start_date'), '%Y-%m-%d').date()
        water_end_date = datetime.strptime(request.form.get('water_end_date'), '%Y-%m-%d').date()

        internet_start_date = datetime.strptime(request.form.get('internet_start_date'), '%Y-%m-%d').date()
        internet_end_date = datetime.strptime(request.form.get('internet_end_date'), '%Y-%m-%d').date()

        utility_split = round((electric + water + internet + household_items)/5, 2)

        summary = {
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

        # creating and saving new utility object
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

        # return redirect(url_for('routes.add_utilities'))
        return render_template('utility.html', utilities=utilities, summary=summary )

    #if no form has been submitted the page will be a blank slate
    return render_template('utility.html', utilities=utilities)

@bp.route('/add_expense', methods=['GET','POST'])
def add_expense():
    if request.method == "POST":
        descriptionList = request.form.getlist('description')
        priceList = request.form.getlist('price')
        dateList = request.form.getlist('date')
        cardList = request.form.getlist('card')

        total_spending = 0

        for i in range(len(priceList)):
            if priceList[i]:
                total_spending += float(priceList[i])

                # SQLite needs the date to be a Python object so we need to convert the string to a datetime object
                date_object = datetime.strptime(dateList[i], '%Y-%m-%d').date()

                new_expense = Expense(
                    description=descriptionList[i],
                    price=float(priceList[i]),
                    card_used=cardList[i],
                    date=date_object
                )

                db.session.add(new_expense)
        
        db.session.commit()
        return render_template('expense.html', total_spending=total_spending)

    return render_template('expense.html', total_spending=0)


@bp.route('/add_gas', methods=['GET','POST'])
def add_gas():
    #when the user submits the form
    if request.method == "POST":

        #gets all the prices from the form as a list of strings
        stationList = request.form.getlist('station')
        priceList = request.form.getlist('price')
        dateList = request.form.getlist('date')
        cardList = request.form.getlist('card')

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

        split_price = round(total_price / 2, 2)

        return render_template('gas.html', split_price=split_price, total_price=total_price)
    
    return render_template('gas.html', split_price=0, total_price=0)

