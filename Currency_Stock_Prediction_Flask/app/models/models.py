from .database import db
from .association_tables import country_regions, country_currencies
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

################### SERVER TABLES #######################
# 1. Countries Table
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(6), nullable=False, unique=True)
    country_name = db.Column(db.String(100), nullable=False)

    regions = relationship(
        'Region',
        secondary=country_regions,
        back_populates='countries'
    )
    currencies = relationship(
        'Currency',
        secondary=country_currencies,
        back_populates='countries'
    )
    companies = relationship(
        'Company',
        back_populates='country',
        cascade='all, delete-orphan'
    )
    exchanges = relationship(
        'Exchange',
        back_populates='country'
    )
    translations = relationship(
        'CountryTranslation',
        back_populates='country',
        cascade='all, delete-orphan'
    )
    gdp_data = relationship(
        'GDPData',
        back_populates='country',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Country {self.country_code} - {self.country_name}>"


# 2. Regions Table
class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String(50), nullable=False, unique=True)

    countries = relationship(
        'Country',
        secondary=country_regions,
        back_populates='regions'
    )

    def __repr__(self):
        return f"<Region {self.region_name}>"


# 4. Currencies Table
class Currency(db.Model):
    __tablename__ = 'currencies'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10))

    countries = relationship(
        'Country',
        secondary=country_currencies,
        back_populates='currencies'
    )
    base_currency_pairs = relationship(
        'CurrencyPair',
        back_populates='base_currency',
        foreign_keys='CurrencyPair.base_currency_id'
    )
    quote_currency_pairs = relationship(
        'CurrencyPair',
        back_populates='quote_currency',
        foreign_keys='CurrencyPair.quote_currency_id'
    )
    accounts = relationship(
        'Account',
        back_populates='base_currency'
    )
    account_currencies = relationship(
        'AccountCurrency',
        back_populates='currency'
    )
    currency_transactions = relationship(
        'AccountCurrencyTransaction',
        back_populates='currency',
        foreign_keys='AccountCurrencyTransaction.currency_id'
    )
    exchange_currency_transactions = relationship(
        'AccountCurrencyTransaction',
        back_populates='exchange_currency',
        foreign_keys='AccountCurrencyTransaction.exchange_currency_id'
    )
    stock_transactions = relationship(
        'AccountStockTransaction',
        back_populates='currency'
    )
    user_preferences = relationship(
        'UserPreference',
        back_populates='default_currency'
    )

    def __repr__(self):
        return f"<Currency {self.code}>"


# 6. Currency_Pairs Table
class CurrencyPair(db.Model):
    __tablename__ = 'currency_pairs'
    id = db.Column(db.Integer, primary_key=True)
    base_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    quote_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)

    base_currency = relationship(
        'Currency',
        back_populates='base_currency_pairs',
        foreign_keys=[base_currency_id]
    )
    quote_currency = relationship(
        'Currency',
        back_populates='quote_currency_pairs',
        foreign_keys=[quote_currency_id]
    )
    data = relationship(
        'CurrencyPairData',
        back_populates='currency_pair',
        cascade='all, delete-orphan'
    )
    predictions = relationship(
        'CurrencyPrediction',
        back_populates='currency_pair',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<CurrencyPair {self.base_currency.code}/{self.quote_currency.code}>"


# 7. Exchanges Table
class Exchange(db.Model):
    __tablename__ = 'exchanges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

    country = relationship('Country', back_populates='exchanges')
    stocks = relationship(
        'Stock',
        back_populates='exchange',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Exchange {self.name}>"


# 8. Companies Table
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_symbol = db.Column(db.String(10), nullable=False, unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    sector = db.Column(db.String(50))
    industry = db.Column(db.String(50))

    country = relationship('Country', back_populates='companies')
    stocks = relationship(
        'Stock',
        back_populates='company',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Company {self.company_symbol} - {self.company_name}>"


# 9. Stocks Table
class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False, unique=True)
    stock_name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'))
    share_class = db.Column(db.String(20))

    company = relationship('Company', back_populates='stocks')
    exchange = relationship('Exchange', back_populates='stocks')
    stock_data = relationship(
        'StockData',
        back_populates='stock',
        cascade='all, delete-orphan'
    )
    predictions = relationship(
        'StockPrediction',
        back_populates='stock',
        cascade='all, delete-orphan'
    )
    account_stocks = relationship(
        'AccountStock',
        back_populates='stock'
    )
    stock_transactions = relationship(
        'AccountStockTransaction',
        back_populates='stock'
    )

    def __repr__(self):
        return f"<Stock {self.stock_symbol} - {self.stock_name}>"


# 10. Stock_Data Table
class StockData(db.Model):
    __tablename__ = 'stock_data'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    open_price = db.Column(db.Numeric(20, 8), nullable=False)
    high_price = db.Column(db.Numeric(20, 8), nullable=False)
    low_price = db.Column(db.Numeric(20, 8), nullable=False)
    close_price = db.Column(db.Numeric(20, 8), nullable=False)
    volume = db.Column(db.Numeric(20, 4), nullable=False)
    day_of_week = db.Column(db.String(10))

    stock = relationship('Stock', back_populates='stock_data')

    def __repr__(self):
        return f"<StockData {self.stock.stock_symbol} at {self.timestamp}>"


# 11. Currency_Pairs_Data Table
class CurrencyPairData(db.Model):
    __tablename__ = 'currency_pairs_data'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    currency_pair_id = db.Column(db.Integer, db.ForeignKey('currency_pairs.id'), nullable=False)
    open_price = db.Column(db.Numeric(20, 8), nullable=False)
    high_price = db.Column(db.Numeric(20, 8), nullable=False)
    low_price = db.Column(db.Numeric(20, 8), nullable=False)
    close_price = db.Column(db.Numeric(20, 8), nullable=False)
    volume = db.Column(db.Numeric(20, 4), nullable=False)
    day_of_week = db.Column(db.String(10))

    currency_pair = relationship('CurrencyPair', back_populates='data')

    def __repr__(self):
        return f"<CurrencyPairData {self.currency_pair} at {self.timestamp}>"


# 12. Stock_Predictions Table
class StockPrediction(db.Model):
    __tablename__ = 'stock_predictions'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    predicted_value = db.Column(db.Numeric(20, 8), nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False)
    model_name = db.Column(db.String(50), nullable=False)

    stock = relationship('Stock', back_populates='predictions')

    def __repr__(self):
        return f"<StockPrediction {self.stock.stock_symbol} on {self.prediction_date}>"


# 13. Currency_Predictions Table
class CurrencyPrediction(db.Model):
    __tablename__ = 'currency_predictions'
    id = db.Column(db.Integer, primary_key=True)
    currency_pair_id = db.Column(db.Integer, db.ForeignKey('currency_pairs.id'), nullable=False)
    predicted_value = db.Column(db.Numeric(20, 8), nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False)
    model_name = db.Column(db.String(50), nullable=False)

    currency_pair = relationship('CurrencyPair', back_populates='predictions')

    def __repr__(self):
        return f"<CurrencyPrediction {self.currency_pair} on {self.prediction_date}>"


# 14. Country_Translations Table
class CountryTranslation(db.Model):
    __tablename__ = 'country_translations'
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    name_common = db.Column(db.String(100), nullable=False)
    name_official = db.Column(db.String(100), nullable=False)

    country = relationship('Country', back_populates='translations')

    def __repr__(self):
        return f"<CountryTranslation {self.country.country_code} in {self.language_code}>"


# 15. GDPData Table
class GDPData(db.Model):
    __tablename__ = 'gdp_data'
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Date, nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    gdp_current_usd = db.Column(db.Numeric(18, 2))
    gdp_growth_rate = db.Column(db.Numeric(5, 2))
    frequency = db.Column(db.Enum('A', 'Q', name='frequency_enum'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('period', 'country_id', name='unique_period_country'),
    )

    country = relationship('Country', back_populates='gdp_data')

    def __repr__(self):
        return f"<GDPData {self.country.country_code} - {self.period}>"


############################ USERS TABLES ############################

# 1. Users Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    accounts = relationship(
        'Account',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    notifications = relationship(
        'UserNotification',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    preferences = relationship(
        'UserPreference',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User {self.email}>"


# 2. Accounts Table
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    public_account_id = db.Column(db.String(16), nullable=False, unique=True)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)  # Base currency
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = relationship('User', back_populates='accounts')
    base_currency = relationship('Currency', back_populates='accounts')
    account_currencies = relationship(
        'AccountCurrency',
        back_populates='account',
        cascade='all, delete-orphan'
    )
    account_stocks = relationship(
        'AccountStock',
        back_populates='account',
        cascade='all, delete-orphan'
    )
    sent_currency_transactions = relationship(
        'AccountCurrencyTransaction',
        back_populates='sender_account',
        foreign_keys='AccountCurrencyTransaction.sender_account_id'
    )
    received_currency_transactions = relationship(
        'AccountCurrencyTransaction',
        back_populates='receiver_account',
        foreign_keys='AccountCurrencyTransaction.receiver_account_id'
    )
    stock_transactions = relationship(
        'AccountStockTransaction',
        back_populates='account',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Account {self.account_name} - User ID {self.user_id}>"


# 3. Account_Currencies Table
class AccountCurrency(db.Model):
    __tablename__ = 'account_currencies'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    balance = db.Column(db.Numeric(20, 8), default=0.0)

    account = relationship('Account', back_populates='account_currencies')
    currency = relationship('Currency', back_populates='account_currencies')

    __table_args__ = (
        db.UniqueConstraint('account_id', 'currency_id', name='unique_account_currency'),
    )

    def __repr__(self):
        return f"<AccountCurrency Account ID {self.account_id} - Currency {self.currency.code}>"


# 4. Account_Stocks Table
class AccountStock(db.Model):
    __tablename__ = 'account_stocks'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    shares = db.Column(db.Numeric(20, 8), default=0.0)

    account = relationship('Account', back_populates='account_stocks')
    stock = relationship('Stock', back_populates='account_stocks')

    __table_args__ = (
        db.UniqueConstraint('account_id', 'stock_id', name='unique_account_stock'),
    )

    def __repr__(self):
        return f"<AccountStock Account ID {self.account_id} - Stock {self.stock.stock_symbol}>"


# 5. Account_Currency_Transactions Table
class AccountCurrencyTransaction(db.Model):
    __tablename__ = 'account_currency_transactions'
    id = db.Column(db.Integer, primary_key=True)
    sender_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    receiver_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    transaction_type = db.Column(
        db.Enum('deposit', 'withdraw', 'transfer', 'exchange', name='currency_transaction_type_enum'), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    exchange_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    exchange_rate = db.Column(db.Numeric(20, 8))
    transaction_fee = db.Column(db.Numeric(20, 8), default=0.0)
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender_account = relationship('Account', back_populates='sent_currency_transactions',
                                  foreign_keys=[sender_account_id])
    receiver_account = relationship('Account', back_populates='received_currency_transactions',
                                    foreign_keys=[receiver_account_id])
    currency = relationship('Currency', back_populates='currency_transactions', foreign_keys=[currency_id])
    exchange_currency = relationship('Currency', back_populates='exchange_currency_transactions',
                                     foreign_keys=[exchange_currency_id])

    def __repr__(self):
        return f"<AccountCurrencyTransaction ID {self.id} - Type {self.transaction_type}>"


# 6. Account_Stock_Transactions Table
class AccountStockTransaction(db.Model):
    __tablename__ = 'account_stock_transactions'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell', name='stock_transaction_type_enum'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    shares = db.Column(db.Numeric(20, 8), nullable=False)
    price_per_share = db.Column(db.Numeric(20, 8), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    transaction_fee = db.Column(db.Numeric(20, 8), default=0.0)
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    account = relationship('Account', back_populates='stock_transactions')
    stock = relationship('Stock', back_populates='stock_transactions')
    currency = relationship('Currency', back_populates='stock_transactions')

    @hybrid_property
    def total_amount(self):
        return self.shares * self.price_per_share

    def __repr__(self):
        return f"<AccountStockTransaction ID {self.id} - Type {self.transaction_type}>"


# 7. User_Notifications Table
class UserNotification(db.Model):
    __tablename__ = 'user_notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = relationship('User', back_populates='notifications')

    def __repr__(self):
        return f"<UserNotification ID {self.id} - User ID {self.user_id}>"


# 8. User_Preferences Table
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    default_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    dark_mode = db.Column(db.Enum('DEFAULT', 'DARK_MODE', 'LIGHT_MODE', name='dark_mode_enum'), default='DEFAULT')
    notifications_enabled = db.Column(db.Boolean, default=True)
    user_language = db.Column(db.Enum('PL', 'EN', name='user_language_enum'), default='EN')

    user = relationship('User', back_populates='preferences')
    default_currency = relationship('Currency', back_populates='user_preferences')

    def __repr__(self):
        return f"<UserPreference User ID {self.user_id}>"
