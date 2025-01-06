import os
import uuid

from django.db import models


def user_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_images', str(instance.user.id), new_filename)

class User(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    profile_image_url = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'



class Region(models.Model):
    region_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'regions'


class Currency(models.Model):
    code = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    data_availability = models.BooleanField(default=False)

    class Meta:
        db_table = 'currencies'



class CurrenciesData(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        db_table = 'currencies_data'
        unique_together = ('currency', 'timestamp')
        indexes = [
            models.Index(fields=['currency', 'timestamp']),
        ]
        ordering = ['-timestamp']


    def __str__(self):
        return f"{self.currency.code} at {self.timestamp}"

class CurrenciesTrainedModels(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE, related_name='currencies_trained_models')
    model_name = models.CharField(max_length=100, default='SeasonalRNN')
    training_date = models.DateTimeField(auto_now_add=True)

    model_file_path = models.CharField(max_length=255, null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
    param_grid = models.JSONField(null=True, blank=True)

    is_latest = models.BooleanField(default=False)

    class Meta:
        db_table = 'currencies_trained_models'



class CurrenciesTrainedModelPrediction(models.Model):
    trained_model = models.ForeignKey('CurrenciesTrainedModels', on_delete=models.CASCADE, related_name='predictions')

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='predictions')
    predicted_value = models.DecimalField(max_digits=20, decimal_places=8)
    prediction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'currencies_trained_model_predictions'
        unique_together = ('trained_model', 'prediction_date')
        ordering = ['-prediction_date']


class Country(models.Model):
    country_code = models.CharField(max_length=6, unique=True)
    country_name = models.CharField(max_length=100)
    regions = models.ManyToManyField(
        Region,
        related_name='countries',
        through='CountryRegion'
    )
    currencies = models.ManyToManyField(
        Currency,
        related_name='countries',
        through='CountryCurrency'
    )

    class Meta:
        db_table = 'countries'


class CountryRegion(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        db_table = 'country_regions'
        unique_together = ('country', 'region')


class CountryCurrency(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    class Meta:
        db_table = 'country_currencies'
        unique_together = ('country', 'currency')


class Exchange(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='exchanges')

    class Meta:
        db_table = 'exchanges'


class Company(models.Model):
    company_symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='companies')
    sector = models.CharField(max_length=50, null=True, blank=True)
    industry = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'companies'


class Stock(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stocks')
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True, related_name='stocks')
    share_class = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'stocks'




class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_data')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=4)

    class Meta:
        db_table = 'stock_data'
        ordering = ['-timestamp']




class StocksTrainedModels(models.Model):
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='stocks_trained_models')
    model_name = models.CharField(max_length=100, default='SeasonalRNN')
    training_date = models.DateTimeField(auto_now_add=True)
    model_file_path = models.CharField(max_length=255,null=True,blank=True)
    metrics = models.JSONField(null=True,blank=True)
    param_grid = models.JSONField(null=True,blank=True)
    is_latest = models.BooleanField(default=False)

    class Meta:
        db_table = 'stocks_trained_models'
        ordering = ['-training_date']

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.model_name} ({self.training_date.strftime('%Y-%m-%d')})"


class StocksTrainedModelPrediction(models.Model):
    trained_model = models.ForeignKey('StocksTrainedModels', on_delete=models.CASCADE, related_name='predictions')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='stock_predictions')
    predicted_value = models.DecimalField(max_digits=20, decimal_places=8)
    prediction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stocks_trained_model_predictions'
        unique_together = ('trained_model', 'prediction_date')
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.prediction_date.strftime('%Y-%m-%d')} : {self.predicted_value}"



class CountryTranslation(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10)
    name_common = models.CharField(max_length=100)
    name_official = models.CharField(max_length=100)

    class Meta:
        unique_together = ('country', 'language_code')
        db_table = 'country_translations'


class GDPData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='gdp_data')
    period_date = models.DateField()
    gdp_current_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    gdp_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    frequency = models.CharField(max_length=1, choices=[('A','A'),('Q','Q')])

    class Meta:
        unique_together = ('period_date', 'country')
        db_table = 'gdp_data'


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    account_name = models.CharField(max_length=100)
    public_account_id = models.CharField(max_length=16, unique=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='accounts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'


class AccountCurrency(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_currencies')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='account_currencies')
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)

    class Meta:
        unique_together = ('account', 'currency')
        db_table = 'account_currencies'


class AccountStock(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_stocks')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='account_stocks')
    shares = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)

    class Meta:
        unique_together = ('account', 'stock')
        db_table = 'account_stocks'


class AccountCurrencyTransaction(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='sent_currency_transactions')
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='received_currency_transactions')
    transaction_type = models.CharField(max_length=10, choices=[('deposit','deposit'),('withdraw','withdraw'),('transfer','transfer'),('exchange','exchange'), ('send', 'send')])
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='currency_transactions')
    exchange_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, related_name='exchange_currency_transactions')
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    default_currency_cost = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_currency_transactions'


class AccountStockTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(max_length=4, choices=[('buy','buy'),('sell','sell')])
    title = models.CharField(max_length=255)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_transactions')
    shares = models.DecimalField(max_digits=20, decimal_places=8)
    price_per_share = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_stock_transactions'


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_display_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='user_preferences')
    dark_mode = models.CharField(max_length=10, choices=[('DEFAULT','DEFAULT'),('DARK_MODE','DARK_MODE'),('LIGHT_MODE','LIGHT_MODE')], default='DEFAULT')
    notifications_enabled = models.BooleanField(default=True)
    user_language = models.CharField(max_length=2, choices=[('PL','PL'),('EN','EN')], default='EN')

    class Meta:
        db_table = 'user_preferences'



class AccountCurrencyValueHistory(models.Model):
    account_currency = models.ForeignKey(AccountCurrency, on_delete=models.CASCADE, related_name='value_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    balance_usd = models.DecimalField(max_digits=30, decimal_places=8)

    class Meta:
        db_table = 'account_currency_value_history'

class AccountStockValueHistory(models.Model):
    account_stock = models.ForeignKey(AccountStock, on_delete=models.CASCADE, related_name='value_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    value_usd = models.DecimalField(max_digits=30, decimal_places=8)

    class Meta:
        db_table = 'account_stock_value_history'