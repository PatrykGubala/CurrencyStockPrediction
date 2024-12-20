from django.core.management.base import BaseCommand

from myapp.services.countries_service import CountriesService


class Command(BaseCommand):
    help = 'Load initial data including currencies, currency_pairs, regions, and countries'

    def handle(self, *args, **options):

        countries_service = CountriesService()
        countries_service.load_all_countries_with_details()