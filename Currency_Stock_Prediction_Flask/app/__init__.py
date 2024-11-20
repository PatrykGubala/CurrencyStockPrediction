from flask import Flask
from .config import Config
from .models.database import db
from .controllers.currency_controller import currency_bp
from .controllers.interest_controller import interest_bp
from .controllers.gdp_controller import gdp_bp
from .controllers.data_loader_controller import data_loader_bp
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(currency_bp)
    app.register_blueprint(interest_bp)
    app.register_blueprint(gdp_bp)
    app.register_blueprint(data_loader_bp)

    return app
