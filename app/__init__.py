from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# initialize database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    # setting to false so that it does not track object changes
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initializing database with the app
    db.init_app(app)

    # migrate is used to update the database based on whatever changes made to the models
    migrate = Migrate(app,db)

    # app.app_context() allows the app to prepare before anything happens like setting up the database
    with app.app_context():

        #blueprint is used to organize all the routes
        from app.routes import bp as routes_bp
        app.register_blueprint(routes_bp)

        # creating the database tables 
        # db.create_all()

    return app



