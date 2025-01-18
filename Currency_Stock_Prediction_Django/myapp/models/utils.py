from .models import Currency

def get_usd_currency_id():
    usd_currency = Currency.query.filter_by(code='USD').first()
    return usd_currency.id if usd_currency else None


