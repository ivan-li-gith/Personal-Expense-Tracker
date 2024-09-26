from flask import Blueprint, render_template, request
from app.models import Gas
from app import db
from datetime import datetime

gas_bp = Blueprint('gas', __name__)

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

@gas_bp.route('/add_gas', methods=['GET','POST'])
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

