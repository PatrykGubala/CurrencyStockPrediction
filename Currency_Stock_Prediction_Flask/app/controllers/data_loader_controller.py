import requests
from flask import Blueprint, jsonify
from ..models.database import db
from ..models.models import Country, Region, Currency, CurrencyPair
from sqlalchemy.exc import IntegrityError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from http.client import IncompleteRead
import logging
import json
from pathlib import Path

data_loader_bp = Blueprint('data_loader', __name__, url_prefix='/api/data-loader')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def fetch_countries_data(api_url='https://restcountries.com/v2/all'):
    session = get_session()
    try:
        logger.info("Fetching data from Rest Countries API (v2)...")
        response = session.get(api_url, timeout=60)
        response.raise_for_status()
        countries_data = response.json()
        logger.info("Data fetched successfully.")
        return countries_data
    except IncompleteRead as e:
        logger.error(f"IncompleteRead error: {e}")
        raise
    except requests.exceptions.RetryError as e:
        logger.error(f"RetryError: {e}")
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise

def load_regions(countries_data):
    regions_cache = {}
    try:
        logger.info("Loading regions...")
        for country in countries_data:
            region_name = country.get('region')
            if region_name:
                if region_name not in regions_cache:
                    region = Region.query.filter_by(region_name=region_name).first()
                    if not region:
                        region = Region(region_name=region_name)
                        db.session.add(region)
                        db.session.flush()
                    regions_cache[region_name] = region
        db.session.commit()
        logger.info("Regions loaded successfully.")
        return regions_cache
    except Exception as e:
        logger.error(f"Error loading regions: {e}")
        db.session.rollback()
        raise

def load_countries(countries_data, regions_cache):
    try:
        logger.info("Loading countries...")
        for country in countries_data:
            country_code = country.get('alpha2Code')
            country_name = country.get('name')
            if not country_code or not country_name:
                continue

            country_obj = Country.query.filter_by(country_code=country_code).first()
            if not country_obj:
                country_obj = Country(country_code=country_code, country_name=country_name)
                db.session.add(country_obj)
                db.session.flush()

            region_name = country.get('region')
            if region_name and region_name in regions_cache:
                region = regions_cache[region_name]
                if region not in country_obj.regions:
                    country_obj.regions.append(region)
        db.session.commit()
        logger.info("Countries loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading countries: {e}")
        db.session.rollback()
        raise

def load_currencies(countries_data):
    currencies_cache = {}
    try:
        logger.info("Loading currencies...")
        for country in countries_data:
            country_code = country.get('alpha2Code')
            if not country_code:
                continue

            currencies = country.get('currencies', [])
            for currency_data in currencies:
                code = currency_data.get('code')
                name = currency_data.get('name')
                symbol = currency_data.get('symbol')

                if not code:
                    continue

                currency = currencies_cache.get(code)
                if not currency:
                    currency = Currency.query.filter_by(code=code).first()
                    if not currency:
                        currency = Currency(code=code, name=name, symbol=symbol)
                        db.session.add(currency)
                        db.session.flush()
                    currencies_cache[code] = currency
        db.session.commit()
        logger.info("Currencies loaded successfully.")
        return currencies_cache
    except Exception as e:
        logger.error(f"Error loading currencies: {e}")
        db.session.rollback()
        raise

def associate_currencies_with_countries(countries_data, currencies_cache):
    try:
        logger.info("Associating currencies with countries...")
        for country in countries_data:
            country_code = country.get('alpha2Code')
            if not country_code:
                continue

            country_obj = Country.query.filter_by(country_code=country_code).first()
            if not country_obj:
                continue

            currencies = country.get('currencies', [])
            for currency_data in currencies:
                code = currency_data.get('code')
                if not code:
                    continue

                currency = currencies_cache.get(code)
                if currency and currency not in country_obj.currencies:
                    country_obj.currencies.append(currency)
        db.session.commit()
        logger.info("Currencies associated with countries successfully.")
    except Exception as e:
        logger.error(f"Error associating currencies with countries: {e}")
        db.session.rollback()
        raise

def create_currency_pairs(usd_id):
    try:
        logger.info("Creating currency pairs with USD as the base currency...")
        currencies = Currency.query.all()
        currency_ids = [currency.id for currency in currencies if
                        currency.id != usd_id]  
        new_pairs = []
        for quote_id in currency_ids:
            existing_pair = CurrencyPair.query.filter_by(
                base_currency_id=usd_id,
                quote_currency_id=quote_id
            ).first()
            if not existing_pair:
                pair = CurrencyPair(
                    base_currency_id=usd_id,
                    quote_currency_id=quote_id
                )
                new_pairs.append(pair)

        if new_pairs:
            db.session.bulk_save_objects(new_pairs)
            db.session.commit()
            logger.info(f"Created {len(new_pairs)} new currency pairs with USD as the base currency.")
        else:
            logger.info("No new currency pairs to create.")
    except Exception as e:
        logger.error(f"Error creating currency pairs: {e}")
        db.session.rollback()
        raise

@data_loader_bp.route('/load', methods=['POST'])
def load_data():
    try:
        countries_data = fetch_countries_data()

        regions_cache = load_regions(countries_data)
        load_countries(countries_data, regions_cache)
        currencies_cache = load_currencies(countries_data)
        associate_currencies_with_countries(countries_data, currencies_cache)

        usd_currency = Currency.query.filter_by(code='USD').first()
        if not usd_currency:
            logger.error("USD currency not found in the database.")
            return jsonify({"error": "USD currency not found in the database."}), 500
        usd_id = usd_currency.id

        create_currency_pairs(usd_id)

        return jsonify({"message": "Data loaded successfully."}), 200

    except IncompleteRead as e:
        logger.error(f"IncompleteRead error: {e}")
        db.session.rollback()
        return jsonify({
            "error": "Incomplete response received from external API.",
            "details": str(e)
        }), 500
    except IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        db.session.rollback()
        return jsonify({
            "error": "Database integrity error.",
            "details": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500