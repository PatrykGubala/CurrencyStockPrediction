from django.apps import AppConfig
from django.db.models.signals import post_migrate
import threading
import logging

logger = logging.getLogger(__name__)

class Config(AppConfig):
    name = 'myapp'

    def ready(self):
        from myapp.services.countries_service import CountriesService

        def load_initial_data(sender, **kwargs):
            def load_data():
                try:
                    countries_service = CountriesService()
                    data = countries_service.fetch_countries_data()
                    countries_service.load_countries_with_details(data)
                    countries_service.create_currency_pairs()
                    logger.info("Initial data loaded successfully.")
                except Exception as e:
                    logger.error(f"Error loading initial data: {e}")

            threading.Thread(target=load_data).start()

        post_migrate.connect(load_initial_data, sender=self)
