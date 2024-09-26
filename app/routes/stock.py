from flask import Blueprint, render_template, request, jsonify
from app.models import Stock
from app import db
from datetime import datetime, timedelta
import yfinance as yf

stock_bp = Blueprint('stock', __name__)

def fetch_stock_data(stock_symbol):
    """
    Takes in a symbol and uses the yfinance library to look up that stock and gets the closing price

    Returns: A dictionary with the stock name and closing price
    """

    stock = yf.Ticker(stock_symbol)     # Creates an instance of Ticker which will contain data about that stock
    stock_data = stock.history(period="1d")     # Gets daily stock data 
    
    # Checks to see if the symbol is valid
    if stock_data.empty:
        raise ValueError(f"Invalid or No data for: {stock_symbol}")
    
    recent_data = stock_data.iloc[-1]       # Goes into the stock_data dataframe and gets data from the last row which is the most recent day 
    current_price = recent_data['Close']        # Gets closing price of stock 
    return {'symbol': stock_symbol, 'price': current_price}

@stock_bp.route('/stock_tracker', methods=['GET', 'POST'])
def stock_tracker():
    """
    Extracts the stock and shares from the form and adds it as a new Stock object into the database.

    Returns: A rendered template of stock.html with the recently added data.
    """

    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol')
        num_shares = request.form.get('num_shares')
        purchase_price = request.form.get('purchase_price')

        new_stock = Stock(
            symbol=stock_symbol,
            shares=num_shares,
            purchase_price=float(stock_data['price']) if stock_data['price'] is not None else 0,
            last_updated=datetime.now()
        )

        db.session.add(new_stock)
        db.session.commit()

    # Fetch all stocks from the database
    fetch_stocks = Stock.query.all()

    # Update stock price if it hasn't been updated in the last hour
    for stock in fetch_stocks:
        if stock.last_updated < datetime.now() - timedelta(hours=1):
            try:
                stock_data = fetch_stock_data(stock.symbol)
                stock.current_price = float(stock_data['price']) if stock_data['price'] is not None else stock.current_price
                stock.last_updated = datetime.now()
                db.session.commit()
            except ValueError as e:
                print(f"Failed to update stock {stock.symbol}: {e}")

    return render_template('stock_tracker.html', stocks=fetch_stocks)