from flask import Blueprint, render_template, request, jsonify
from app.models import Stock, Investment_History
from app import db
from datetime import datetime, timedelta
import yfinance as yf

stock_bp = Blueprint('stock', __name__)

def get_stock_data(symbol):
    """
    Takes in a symbol and uses the yfinance library to look up that stock and gets the closing price
    Returns: A dictionary with the stock name and closing price
    """
    stock = yf.Ticker(symbol)                               # Creates an instance of Ticker which will contain data about that stock
    stock_data = stock.history(period="1d")                 # Gets daily stock data 
    recent_data = stock_data.iloc[-1]                       # Goes into the stock_data dataframe and gets data from the last row which is the most recent day 
    current_price = round(recent_data['Close'], 2)          # Gets closing price of stock 
    return {'symbol': symbol, 'price': current_price}


def update_investment_history():
    current_date = datetime.now().date()

    # stock_db = []
    # for stock in Stock.query.all():
    #     if stock.last_updated.date() == current_date:
    #         stock_db.append(stock)

    stock_db = [stock for stock in Stock.query.all() if stock.last_updated.date() == current_date]      # Cleaner way to write whats above

    # No entries in db with todays current date return empty lists
    if len(stock_db) == 0:  
        return [], [], [], []  
    
    # Calculating investment values and percent values and handling if initial investment is 0
    eod_initial_investment = sum(entry.purchase_price * entry.shares for entry in stock_db)
    eod_investment = sum(entry.current_price * entry.shares for entry in stock_db)
    if eod_initial_investment != 0:
        percent_diff = (eod_investment - eod_initial_investment) / eod_initial_investment * 100
    else:
        percent_diff = 0

    exists_in_db = Investment_History.query.filter_by(date=current_date).first()      # Finds an entry for todays date

    # If an entry for todays date exists, update it else create a new investment history object
    if exists_in_db:
        exists_in_db.eod_initial_investment = eod_initial_investment
        exists_in_db.eod_investment = eod_investment
        exists_in_db.percent_diff = percent_diff
        db.session.commit()
    else:
        new_investment_history = Investment_History(
            date=current_date,
            eod_initial_investment=round(eod_initial_investment, 2),
            eod_investment=round(eod_investment, 2),
            percent_diff=round(percent_diff, 2)
        )
        db.session.add(new_investment_history)
        db.session.commit()

    investment_history_db = Investment_History.query.all()
    date_list = [entry.date.strftime("%m/%d") for entry in investment_history_db]
    eod_initial_investment_list = [entry.eod_initial_investment for entry in investment_history_db]
    eod_investment_list = [entry.eod_investment for entry in investment_history_db]
    percent_diff_list =[entry.percent_diff for entry in investment_history_db]

    return date_list, eod_initial_investment_list, eod_investment_list, percent_diff_list

@stock_bp.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    """
    If a form is submitted, fetch the data from the form and create a Stock object if it does not already exist in db. 
    Also update each stock hourly with the current price 
    Returns: A rendered html page with the database, list of dates/ daily investments, and initial investments
    """
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        shares = float(request.form.get('shares'))
        purchase_price = float(request.form.get('purchase_price'))

        # Grabs stock data and gets its current price
        stock_data = get_stock_data(symbol)
        current_price = stock_data['price']

        # Check if stock exists in db. If it does update it else add into db
        exists_in_db = Stock.query.filter_by(symbol=symbol).first()     # Filters by stock. .first() looks for the first entry matching it (also ensures there is only entry per stock)
        if exists_in_db:
            # total_shares = exists_in_db.shares + shares
            average_purchase_price = ((exists_in_db.purchase_price * exists_in_db.shares) + (purchase_price * shares)) / (exists_in_db.shares + shares)
            exists_in_db.shares = exists_in_db.shares + shares
            exists_in_db.purchase_price = round(average_purchase_price, 2)
            exists_in_db.current_price = current_price
            exists_in_db.last_updated = datetime.now()
            db.session.commit()
        else:
            new_stock = Stock(
                symbol=symbol,
                shares=shares,
                purchase_price=purchase_price,
                current_price=current_price,
                last_updated=datetime.now()
            )
            db.session.add(new_stock)
            db.session.commit()
    
        date_list, eod_initial_investment_list, eod_investment_list, percent_diff_list = update_investment_history()

        # Check if it's an AJAX request by looking for the `ajax=true` parameter
        if request.args.get('ajax') == 'true':
            return jsonify({
                'date_list': date_list,
                'eod_initial_investment_list': eod_initial_investment_list,
                'eod_investment_list': eod_investment_list,
                'percent_diff_list': percent_diff_list
            })
        else:
            return render_template(
                'stock_tracker.html', 
                stocks=Stock.query.all(),
                date_list=date_list,
                eod_initial_investment_list=eod_initial_investment_list, 
                eod_investment_list=eod_investment_list, 
                percent_diff_list=percent_diff_list
            )
    
    stock_db = Stock.query.all()
    date_list, eod_initial_investment_list, eod_investment_list, percent_diff_list = update_investment_history()

    # Update stock prices if older than 1 hour and calculate total investments
    # for entry in stock_db:
    #     if entry.last_updated < datetime.now() - timedelta(hours=1):
    #         stock_data = get_stock_data(entry.symbol)
    #         entry.current_price = float(stock_data['price'])
    #         entry.last_updated = datetime.now()
    #         db.session.commit()
    
    # If no form is submitted, get data for the graph and render it to the html page
    return render_template(
        'stock_tracker.html', 
        stocks=Stock.query.all(),
        date_list=date_list,
        eod_initial_investment_list=eod_initial_investment_list, 
        eod_investment_list=eod_investment_list, 
        percent_diff_list=percent_diff_list
    )

@stock_bp.route('/update_portfolio', methods=['GET'])
def updatePortfolio():
    """
    Loops through the db and adds each stocks info into a list of dictionaries
    Returns: A JSON list of all existing stocks and their info
    """
    stock_db = Stock.query.all()
    # stock_data_json = []
    # for entry in stock_db:
    #     stock_data_json.append({
    #         'symbol': entry.symbol,
    #         'shares': entry.shares,
    #         'purchase_price': entry.purchase_price,
    #         'current_price': entry.current_price,
    #         'gain_loss': round((entry.current_price - entry.purchase_price) * entry.shares, 2),
    #         'percentage': round(((entry.current_price - entry.purchase_price) / entry.purchase_price) * 100, 2)
    #     })

    # Cleaner way to write whats above
    stock_data_json = [{
        'symbol': entry.symbol,
        'shares': entry.shares,
        'purchase_price': entry.purchase_price,
        'current_price': entry.current_price,
        'gain_loss': round((entry.current_price - entry.purchase_price) * entry.shares, 2),
        'percentage': round(((entry.current_price - entry.purchase_price) / entry.purchase_price) * 100, 2)
    } for entry in stock_db]

    return jsonify({'stocks': stock_data_json})

@stock_bp.route('/update_stock_chart', methods=['GET'])
def update_stock_chart():
    """
    heonstly this is to handle multiple entries of the same day. 
    An AJAX request is sent to this route to update the stock chart with the most recent entries from the database. It grabs 
    """
    # current_date = datetime.now()
    # stock_db = Stock.query.all()
    # updated_initial_investments = sum(entry.purchase_price * entry.shares for entry in stock_db)      # Calculating total initial investments
    # updated_total_investments = sum(entry.current_price * entry.shares for entry in stock_db)         # Calculating total investments from current price of each stock

    # # total_investments_ytd[0] = 53000

    # # If the last entry is the same day as today, update the lists with the updated values 
    # if ytd_dates[-1] == current_date:
    #     total_initial_investments =  updated_initial_investments
    #     total_investments_ytd[-1] = updated_total_investments

    date_list, eod_initial_investment_list, eod_investment_list, percent_diff_list = update_investment_history()
    return jsonify({
        'date_list': date_list,
        'eod_initial_investment_list': eod_initial_investment_list,
        'eod_investment_list': eod_investment_list,
        'percent_diff_list': percent_diff_list
    })
