from django.test import TestCase
from unittest.mock import patch, MagicMock
from myapp.models import Country
from myapp.services.countries_service import CountriesService

class CountriesServiceTestCase(TestCase):
    def setUp(self):
        self.service = CountriesService()

    @patch('myapp.services.countries_service.requests.get')
    def test_fetch_countries_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"alpha2Code": "FR", "name": "France"},
            {"alpha2Code": "DE", "name": "Germany"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = self.service.fetch_countries_data(api_url='http://fakeurl.com')
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['alpha2Code'], 'FR')
        self.assertEqual(data[1]['alpha2Code'], 'DE')


    @patch('myapp.services.countries_service.requests.get')
    def test_load_only_countries(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"alpha2Code": "FR", "name": "France"},
            {"alpha2Code": "DE", "name": "Germany"},
            {"alpha2Code": None, "name": "NoCodeCountry"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = self.service.fetch_countries_data()
        self.service.load_only_countries(data)
        france = Country.objects.filter(country_code="FR").first()
        germany = Country.objects.filter(country_code="DE").first()
        no_code = Country.objects.filter(country_name="NoCodeCountry").first()

        self.assertIsNotNone(france)
        self.assertIsNotNone(germany)
        self.assertIsNone(no_code)


    @patch('myapp.services.countries_service.requests.get')
    def test_load_countries_with_details(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "alpha2Code": "FR",
                "name": "France",
                "region": "Europe",
                "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}]
            },
            {
                "alpha2Code": "DE",
                "name": "Germany",
                "region": "Europe",
                "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}]
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        self.service.load_all_data()
        france = Country.objects.filter(country_code="FR").first()
        germany = Country.objects.filter(country_code="DE").first()
        self.assertIsNotNone(france)
        self.assertIsNotNone(germany)
        self.assertEqual(france.regions.first().region_name, "Europe")
        self.assertEqual(germany.regions.first().region_name, "Europe")
        self.assertTrue(france.currencies.filter(code="EUR").exists())
        self.assertTrue(germany.currencies.filter(code="EUR").exists())


    def test_get_all_countries_dto(self):
        Country.objects.create(country_code="US", country_name="United States")
        Country.objects.create(country_code="GB", country_name="United Kingdom")
        result = self.service.get_all_countries_dto()
        self.assertEqual(len(result), 2)
        codes = [item['country_code'] for item in result]
        self.assertIn("US", codes)
        self.assertIn("GB", codes)


    def test_get_country_by_code_dto(self):
        Country.objects.create(country_code="IT", country_name="Italy")
        italy = self.service.get_country_by_code_dto("IT")
        self.assertEqual(italy['country_code'], "IT")
        self.assertEqual(italy['country_name'], "Italy")

        no_country = self.service.get_country_by_code_dto("ZZ")
        self.assertIsNone(no_country)