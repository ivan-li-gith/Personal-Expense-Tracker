from flask import Blueprint, render_template, request, jsonify
from app.models import Stock
from app import db
from datetime import datetime, timedelta
import yfinance as yf

stock_bp = Blueprint('stock', __name__)

def fetch_stock_data(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    stock_info = stock.history(period="1d")  # Fetch daily stock data
    
    if stock_info.empty:
        raise ValueError(f"No data found for symbol: {stock_symbol}")
    
    latest_data = stock_info.iloc[-1]  # Get the latest row of data
    current_price = latest_data['Close']  # Use the 'Close' column for the current price
    return {'symbol': stock_symbol, 'price': current_price}

@stock_bp.route('/stock_tracker', methods=['GET', 'POST'])
def stock_tracker():
    if request.method == 'POST':
        stock_symbol = request.form.get('symbol')
        num_shares = request.form.get('shares')

        try:
            stock_data = fetch_stock_data(stock_symbol)
        except ValueError as e:
            return f"Error: {e}", 400  # Handle invalid symbols or no data

        # Add the stock to the database
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