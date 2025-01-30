from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from myapp.models import Country


class CountriesIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('myapp.services.countries_service.requests.get')
    def test_load_only_countries_integration(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"alpha2Code": "FR", "name": "France"},
            {"alpha2Code": "DE", "name": "Germany"}
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = self.client.get(reverse('load_only_countries'))
        self.assertEqual(response.status_code, 405)
        response = self.client.post(reverse('load_only_countries'))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual("Tylko kraje zostały załadowane pomyślnie", json_data["message"])


        self.assertTrue(Country.objects.filter(country_code="FR").exists())
        self.assertTrue(Country.objects.filter(country_code="DE").exists())

    @patch('myapp.services.countries_service.requests.get')

    def test_load_countries_with_details_integration(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "alpha2Code": "FR",
                "name": "France",
                "region": "Europe",
                "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€"}]
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = self.client.get(reverse('load_countries_with_details'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('load_countries_with_details'))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual("Kraje wraz z regionami i walutami zostały załadowane pomyślnie", json_data["message"])

        france = Country.objects.filter(country_code="FR").first()
        self.assertIsNotNone(france)
        self.assertTrue(france.regions.filter(region_name="Europe").exists())
        self.assertTrue(france.currencies.filter(code="EUR").exists())

    def test_get_all_countries_integration(self):
        Country.objects.create(country_code="US", country_name="United States")
        Country.objects.create(country_code="GB", country_name="United Kingdom")

        response = self.client.get(reverse('get_all_countries'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("countries", data)
        countries_list = data["countries"]
        self.assertEqual(len(countries_list), 2)

        codes = [code["country_code"] for code in countries_list]
        self.assertIn("US", codes)
        self.assertIn("GB", codes)

    def test_get_country_integration(self):
        Country.objects.create(country_code="IT", country_name="Italy")
        url_found = reverse('get_country', args=["IT"])
        url_not_found = reverse('get_country', args=["ZZ"])

        response_found = self.client.get(url_found)
        self.assertEqual(response_found.status_code, 200)
        data_found = response_found.json()
        self.assertIn("country", data_found)
        self.assertEqual(data_found["country"]["country_code"], "IT")

        response_not_found = self.client.get(url_not_found)
        self.assertEqual(response_not_found.status_code, 404)
        data_not_found = response_not_found.json()
        self.assertIn("Kraj nie został znaleziony", data_not_found["error"])
