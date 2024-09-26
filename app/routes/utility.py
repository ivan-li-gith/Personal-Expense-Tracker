from flask import Blueprint, render_template, request, jsonify
from app.models import Utility
from app import db
from datetime import datetime

utilities_bp = Blueprint('utilities', __name__)

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

@utilities_bp.route('/utilities', methods=['GET', 'POST'])
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
    
    return render_template('utility.html', utilities=utilities)

@utilities_bp.route('/redraw_utility_chart', methods=['GET'])
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