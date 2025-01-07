import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class RegionsIntegrationTests(APITestCase):
    def setUp(self):
        self.create_url = reverse('create_region')
        self.list_url = reverse('get_all_regions')

    def test_create_region(self):
        payload = {"region_name": "ATLANTYDA"}
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("region", response.json())
        self.assertEqual(response.json()["region"]["region_name"], "ATLANTYDA")

    def test_get_all_regions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("regions", response.json())