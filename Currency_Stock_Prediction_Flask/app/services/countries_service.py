from typing import List, Optional
import requests
from app.repositories.countries_repository import CountriesRepository
from app.services.regions_service import RegionsService
from app.services.currencies_service import CurrenciesService
from app.repositories.currency_pairs_repository import CurrencyPairsRepository
from app.models.dtos import CountryDTO
from app.utils.logger import setup_logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from http.client import IncompleteRead

class CountriesService:
    def __init__(self):
        self.countries_repo = CountriesRepository()
        self.regions_service = RegionsService()
        self.currencies_service = CurrenciesService()
        self.currency_pairs_repo = CurrencyPairsRepository()
        self.logger = setup_logger(__name__)

    def get_session(self) -> requests.Session:
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

    def fetch_countries_data(self, api_url: str = 'https://restcountries.com/v2/all') -> List[dict]:
        session = self.get_session()
        try:
            self.logger.info("Pobieranie danych z API Rest Countries...")
            response = session.get(api_url, timeout=60)
            response.raise_for_status()
            countries_data = response.json()
            self.logger.info("Dane zostały pobrane pomyślnie.")
            return countries_data
        except IncompleteRead as e:
            self.logger.error(f"Niekompletne dane: {e}")
            raise
        except requests.exceptions.RetryError as e:
            self.logger.error(f"Błąd retry: {e}")
            raise
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Przekroczono limit czasu: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Błąd żądania: {e}")
            raise

    def load_only_countries(self, countries_data: List[dict]):
        try:
            self.logger.info("Ładowanie tylko krajów...")
            for country in countries_data:
                country_code = country.get('alpha2Code')
                country_name = country.get('name')
                if not country_code or not country_name:
                    continue

                existing_country = self.countries_repo.get_country_by_code(country_code)
                if not existing_country:
                    self.countries_repo.add_country(country_code, country_name)
            self.logger.info("Kraje zostały załadowane pomyślnie.")
        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania krajów: {e}")
            raise

    def load_countries_with_details(self, countries_data: List[dict]):
        try:
            self.logger.info("Ładowanie krajów wraz z regionami i walutami")
            for country in countries_data:
                country_code = country.get('alpha2Code')
                country_name = country.get('name')
                if not country_code or not country_name:
                    continue

                existing_country = self.countries_repo.get_country_by_code(country_code)
                if not existing_country:
                    existing_country = self.countries_repo.add_country(country_code, country_name)

                region_name = country.get('region')
                if region_name:
                    region_dto = self.regions_service.add_region(region_name)
                    region = self.regions_service.regions_repo.get_region_by_name(region_name)
                    if region:
                        self.countries_repo.associate_region_to_country(existing_country.id, region.id)

                currencies = country.get('currencies', [])
                for currency_data in currencies:
                    code = currency_data.get('code')
                    name = currency_data.get('name')
                    symbol = currency_data.get('symbol')
                    if not code or not name:
                        continue

                    currency_dto = self.currencies_service.add_currency(code, name, symbol)
                    currency = self.currencies_service.currencies_repo.get_currency_by_code(code)
                    if currency:
                        self.countries_repo.associate_currency_to_country(existing_country.id, currency.id)

            self.logger.info("Kraje wraz z regionami i walutami zostały załadowane pomyślnie.")
        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania krajów z detalami: {e}")
            raise

    def create_currency_pairs(self):
        try:
            self.logger.info("Tworzenie par walutowych z USD jako walutą bazową")
            usd_currency = self.currencies_service.currencies_repo.get_currency_by_code('USD')
            if not usd_currency:
                self.logger.error("Waluta USD nie została znaleziona w bazie danych.")
                raise ValueError("Waluta USD nie została znaleziona w bazie danych.")

            currencies = self.currencies_service.currencies_repo.get_all_currencies()
            for currency in currencies:
                if currency.id == usd_currency.id:
                    continue
                existing_pair = self.currency_pairs_repo.get_currency_pair(usd_currency.id, currency.id)
                if not existing_pair:
                    self.currency_pairs_repo.add_currency_pair(usd_currency.id, currency.id)
            self.logger.info("Par walutowych zostały utworzone pomyślnie.")
        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia par walutowych: {e}")
            raise

    def get_all_countries_dto(self) -> List[CountryDTO]:
        countries = self.countries_repo.get_all_countries()
        countries_dto = []
        for country in countries:
            country_dict: CountryDTO = {
                "id": country.id,
                "country_code": country.country_code,
                "country_name": country.country_name,
                "regions": [
                    {"id": region.id, "region_name": region.region_name}
                    for region in country.regions
                ],
                "currencies": [
                    {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}
                    for currency in country.currencies
                ]
            }
            countries_dto.append(country_dict)
        return countries_dto

    def get_country_by_code_dto(self, country_code: str) -> Optional[CountryDTO]:
        country = self.countries_repo.get_country_by_code(country_code)
        if not country:
            return None
        country_dto: CountryDTO = {
            "id": country.id,
            "country_code": country.country_code,
            "country_name": country.country_name,
            "regions": [
                {"id": region.id, "region_name": region.region_name}
                for region in country.regions
            ],
            "currencies": [
                {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}
                for currency in country.currencies
            ]
        }
        return country_dto

    def load_all_data(self):
        countries_data = self.fetch_countries_data()
        self.load_countries_with_details(countries_data)
        self.create_currency_pairs()
