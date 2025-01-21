import os
import uuid

from django.db import models
from rest_framework.exceptions import ValidationError


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

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    title = models.CharField(max_length=100)
    public_account_id = models.CharField(max_length=16)
    account_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'contacts'
        unique_together = ('user', 'public_account_id')

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
        constraints = [
            models.UniqueConstraint(
                fields=['currency', 'is_latest'],
                name='unique_latest_currency_model'
            )
        ]


class CurrenciesPrediction(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='predictions')
    predicted_value = models.DecimalField(max_digits=20, decimal_places=8)
    prediction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'currencies_predictions'
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
    company_name = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='companies', null=True, blank=True)
    logo_url = models.URLField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'companies'


class Stock(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stocks')
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True, related_name='stocks')
    share_class = models.CharField(max_length=20, null=True, blank=True)
    data_availability = models.BooleanField(default=False)

    class Meta:
        db_table = 'stocks'



class StocksData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stocks_data')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        db_table = 'stocks_data'
        ordering = ['-timestamp']
        unique_together = ('stock', 'timestamp')


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
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'is_latest'],
                name='unique_latest_stock_model'
            )
        ]

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.model_name} ({self.training_date.strftime('%Y-%m-%d')})"


class StocksPrediction(models.Model):
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='stocks_predictions')
    predicted_value = models.DecimalField(max_digits=20, decimal_places=8)
    prediction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stocks_predictions'
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.prediction_date.strftime('%Y-%m-%d')} : {self.predicted_value}"




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
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='non_negative_balance'
            )
        ]


class AccountStock(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_stocks')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='account_stocks')
    shares = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)

    class Meta:
        unique_together = ('account', 'stock')
        db_table = 'account_stocks'

        constraints = [
            models.CheckConstraint(
                check=models.Q(shares__gte=0),
                name='non_negative_shares'
            )
        ]



class CurrenciesTransactionType(models.TextChoices):
    DEPOSIT = 'deposit', 'Deposit'
    WITHDRAW = 'withdraw', 'Withdraw'
    BUY = 'buy', 'Buy'
    SELL = 'sell', 'Sell'
    SEND = 'send', 'Send'


class AccountCurrencyTransaction(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True,blank=True,  related_name='sent_currency_transactions')
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True,blank=True,  related_name='received_currency_transactions')
    transaction_type = models.CharField(
        max_length=10,
        choices=CurrenciesTransactionType.choices
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='currency_transactions')
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    default_currency_cost = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_currency_transactions'

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be positive")


class StocksTransactionType(models.TextChoices):
    BUY = 'buy', 'Buy'
    SELL = 'sell', 'Sell'

class AccountStockTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(
        max_length=4,
        choices=StocksTransactionType.choices
    )
    title = models.CharField(max_length=255)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_transactions')
    shares = models.DecimalField(max_digits=20, decimal_places=8)
    price_per_share = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='stock_transactions')
    default_currency_cost = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    transaction_fee = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'account_stock_transactions'

    def clean(self):
        if self.shares <= 0:
            raise ValidationError("Shares must be positive")


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'



