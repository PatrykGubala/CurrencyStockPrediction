from flask import Flask
from .config import Config
from .controllers.countries_controller import countries_bp
from .controllers.currencies_controller import currencies_bp
from .controllers.currency_pairs_controller import currency_pairs_bp
from .controllers.regions_controller import regions_bp
from .models.database import db
from .controllers.data_loader_controller import data_loader_bp
from .controllers.user_controller import user_bp
from flask_session import Session
from dotenv import load_dotenv
from flask_migrate import Migrate
import firebase_admin
from firebase_admin import credentials

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    cred = credentials.Certificate(app.config['FIREBASE_ADMIN_CREDENTIALS'])
    firebase_admin.initialize_app(cred)

    db.init_app(app)
    app.config['SESSION_SQLALCHEMY'] = db
    Session(app)
    migrate = Migrate(app, db)

    app.register_blueprint(user_bp)
    app.register_blueprint(data_loader_bp)
    app.register_blueprint(countries_bp)
    app.register_blueprint(regions_bp)
    app.register_blueprint(currencies_bp)
    app.register_blueprint(currency_pairs_bp)


    return app
