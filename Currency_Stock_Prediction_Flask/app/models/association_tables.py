from .database import db

country_regions = db.Table(
    'country_regions',
    db.Column('country_id', db.Integer, db.ForeignKey('countries.id'), primary_key=True),
    db.Column('region_id', db.Integer, db.ForeignKey('regions.id'), primary_key=True)
)

country_currencies = db.Table(
    'country_currencies',
    db.Column('country_id', db.Integer, db.ForeignKey('countries.id'), primary_key=True),
    db.Column('currency_id', db.Integer, db.ForeignKey('currencies.id'), primary_key=True)
)

