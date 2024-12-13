from typing import Optional, List
from myapp.models import Country, Region, Currency, CountryRegion, CountryCurrency

class CountriesRepository:
    def get_country_by_code(self, country_code: str) -> Optional[Country]:
        return Country.objects.filter(country_code=country_code).first()

    def get_all_countries(self) -> List[Country]:
        return list(Country.objects.all())

    def add_country(self, country_code: str, country_name: str) -> Country:
        country, created = Country.objects.get_or_create(
            country_code=country_code,
            defaults={'country_name': country_name}
        )
        return country

    def associate_region_to_country(self, country: Country, region: Region):
        CountryRegion.objects.get_or_create(country=country, region=region)

    def associate_currency_to_country(self, country: Country, currency: Currency):
        CountryCurrency.objects.get_or_create(country=country, currency=currency)
