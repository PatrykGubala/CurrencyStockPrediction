from django.test import TestCase
from unittest.mock import patch, MagicMock
from myapp.models import Country, Region, Currency, CountryRegion, CountryCurrency
from myapp.repositories.countries_repository import CountriesRepository
from myapp.services.countries_service import CountriesService


class CountriesRepositoryTestCase(TestCase):
    def setUp(self):
        self.repository = CountriesRepository()
        self.country_code = "PL"
        self.country_name = "Poland"
        self.country = self.repository.add_country(self.country_code, self.country_name)

    def test_add_country(self):
        retrieved_country = self.repository.get_country_by_code(self.country_code)
        self.assertIsNotNone(retrieved_country)
        self.assertEqual(retrieved_country.country_code, self.country_code)
        self.assertEqual(retrieved_country.country_name, self.country_name)

    def test_associate_region_to_country(self):
        region = Region.objects.create(region_name="Europe")
        self.repository.associate_region_to_country(self.country, region)
        self.assertTrue(
            CountryRegion.objects.filter(country=self.country, region=region).exists()
        )

    def test_associate_currency_to_country(self):
        currency = Currency.objects.create(code="PLN", name="Polish Zloty")
        self.repository.associate_currency_to_country(self.country, currency)
        self.assertTrue(
            CountryCurrency.objects.filter(country=self.country, currency=currency).exists()
        )

    def test_add_and_remove_non_existent_country(self):
        self.assertIsNone(
            self.repository.get_country_by_code("ZZ")
        )
        country = self.repository.add_country("ZZ", "Fakeland")
        self.assertIsNotNone(country.id)
        self.assertIsNotNone(
            self.repository.get_country_by_code("ZZ")
        )
        country.delete()
        self.assertIsNone(
            self.repository.get_country_by_code("ZZ")
        )
