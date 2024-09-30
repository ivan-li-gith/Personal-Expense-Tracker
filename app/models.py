from app import db

# each class is a table in the database
# each of the class attributes represent columns in the table
# the id is basically a row identifier
# nullable = False means it cannot be Null and must have a value
class Utility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    electric = db.Column(db.Float, nullable=False)
    water = db.Column(db.Float, nullable=False)
    internet = db.Column(db.Float, nullable=False)
    household_item = db.Column(db.Float, nullable=False)
    # date = db.Column(db.Date, nullable=False)
    # Billing periods for each utility
    electric_start_date = db.Column(db.Date, nullable=False)
    electric_end_date = db.Column(db.Date, nullable=False)
    water_start_date = db.Column(db.Date, nullable=False)
    water_end_date = db.Column(db.Date, nullable=False)
    internet_start_date = db.Column(db.Date, nullable=False)
    internet_end_date = db.Column(db.Date, nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    card_used = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

class Gas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    card_used = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False) 

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)

class Investment_History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False) 
    eod_initial_investment = db.Column(db.Float, nullable=False)
    eod_investment = db.Column(db.Float, nullable=False)
    percent_diff = db.Column(db.Float, nullable=False)


    


