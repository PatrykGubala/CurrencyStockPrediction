import requests
from typing import List, Optional
from myapp.repositories.countries_repository import CountriesRepository
from myapp.repositories.regions_repository import RegionsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.repositories.currency_pairs_repository import CurrencyPairsRepository

class CountriesService:
    def __init__(self):
        self.countries_repo = CountriesRepository()
        self.regions_repo = RegionsRepository()
        self.currencies_repo = CurrenciesRepository()
        self.currency_pairs_repo = CurrencyPairsRepository()

    def fetch_countries_data(self, api_url='https://restcountries.com/v2/all') -> List[dict]:
        response = requests.get(api_url, timeout=60)
        response.raise_for_status()
        return response.json()

    def load_only_countries(self, countries_data: List[dict]):
        for country in countries_data:
            country_code = country.get('alpha2Code')
            country_name = country.get('name')
            if country_code and country_name:
                existing_country = self.countries_repo.get_country_by_code(country_code)
                if not existing_country:
                    self.countries_repo.add_country(country_code, country_name)

    def load_countries_with_details(self, countries_data: List[dict]):
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
                region = self.regions_repo.get_region_by_name(region_name)
                if not region:
                    region = self.regions_repo.add_region(region_name)
                self.countries_repo.associate_region_to_country(existing_country, region)

            currencies = country.get('currencies', [])
            for cdata in currencies:
                code = cdata.get('code')
                cname = cdata.get('name')
                symbol = cdata.get('symbol')
                if code and cname:
                    currency = self.currencies_repo.get_currency_by_code(code)
                    if not currency:
                        currency = self.currencies_repo.add_currency(code, cname, symbol)
                    self.countries_repo.associate_currency_to_country(existing_country, currency)

    def create_currency_pairs(self):
        usd_currency = self.currencies_repo.get_currency_by_code('USD')
        if not usd_currency:
            raise ValueError("USD not found")

        currencies = self.currencies_repo.get_all_currencies()
        for currency in currencies:
            if currency.id == usd_currency.id:
                continue
            if not self.currency_pairs_repo.get_currency_pair(usd_currency.id, currency.id):
                self.currency_pairs_repo.add_currency_pair(usd_currency.id, currency.id)

    def get_all_countries_dto(self) -> List[dict]:
        countries = self.countries_repo.get_all_countries()
        result = []
        for country in countries:
            result.append({
                "id": country.id,
                "country_code": country.country_code,
                "country_name": country.country_name,
                "regions": [
                    {"id": region.id, "region_name": region.region_name}
                    for region in country.regions.all()
                ],
                "currencies": [
                    {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}
                    for currency in country.currencies.all()
                ]
            })
        return result

    def get_country_by_code_dto(self, country_code: str) -> Optional[dict]:
        country = self.countries_repo.get_country_by_code(country_code)
        if not country:
            return None
        return {
            "id": country.id,
            "country_code": country.country_code,
            "country_name": country.country_name,
            "regions": [
                {"id": region.id, "region_name": region.region_name}
                for region in country.regions.all()
            ],
            "currencies": [
                {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}
                for currency in country.currencies.all()
            ]
        }

    def load_all_data(self):
        data = self.fetch_countries_data()
        self.load_countries_with_details(data)
        self.create_currency_pairs()
