from typing import List, Optional
from app.models.models import Country, Currency, Region
from app.models.database import db

class CountriesRepository:
    def get_country_by_code(self, country_code: str) -> Optional[Country]:
        return Country.query.filter_by(country_code=country_code).first()

    def get_country_by_id(self, country_id: int) -> Optional[Country]:
        return Country.query.get(country_id)

    def get_all_countries(self) -> List[Country]:
        return Country.query.all()

    def add_country(self, country_code: str, country_name: str) -> Country:
        country = Country(country_code=country_code, country_name=country_name)
        db.session.add(country)
        db.session.commit()
        return country

    def update_country(self, country_id: int, new_name: str) -> Optional[Country]:
        country = self.get_country_by_id(country_id)
        if country:
            country.country_name = new_name
            db.session.commit()
        return country

    def delete_country(self, country_id: int) -> bool:
        country = self.get_country_by_id(country_id)
        if country:
            db.session.delete(country)
            db.session.commit()
            return True
        return False

    def associate_region_to_country(self, country_id: int, region_id: int) -> None:
        country = self.get_country_by_id(country_id)
        if country:
            region = Region.query.get(region_id)
            if region and region not in country.regions:
                country.regions.append(region)
                db.session.commit()

    def associate_currency_to_country(self, country_id: int, currency_id: int) -> None:
        country = self.get_country_by_id(country_id)
        if country:
            currency = Currency.query.get(currency_id)
            if currency and currency not in country.currencies:
                country.currencies.append(currency)
                db.session.commit()