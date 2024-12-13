from .models import CurrencyPair, CurrencyPairData, Currency

def get_usd_currency_id():
    usd_currency = Currency.query.filter_by(code='USD').first()
    return usd_currency.id if usd_currency else None


def convert_currency(amount_usd, user):
    display_currency = user.preferences.default_display_currency
    if display_currency.code == 'USD':
        return amount_usd
    exchange_pair = CurrencyPair.query.filter_by(base_currency_id=get_usd_currency_id(), quote_currency_id=display_currency.id).first()
    if exchange_pair and exchange_pair.data:
        latest_data = CurrencyPairData.query.filter_by(currency_pair_id=exchange_pair.id).order_by(CurrencyPairData.timestamp.desc()).first()
        if latest_data:
            return float(amount_usd) * float(latest_data.close_price)
    return amount_usd
