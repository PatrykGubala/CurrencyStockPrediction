from django.apps import AppConfig
from django.db.models.signals import post_migrate
import threading
import logging

logger = logging.getLogger(__name__)

class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from myapp.models import Stock, Country
        from myapp.services.countries_service import CountriesService
        from myapp.services.stocks_loader_service import PolygonStocksLoaderService

        import sys
        if 'runserver' not in sys.argv:
            return

        try:

            countries_count = Country.objects.count()
            if countries_count <= 1:
                logger.info("No countries found in database. Loading initial countries data...")
                countries_service = CountriesService()
                countries_service.load_all_data()
                logger.info(f"Successfully loaded countries data")
            else:
                logger.info(f"Found {countries_count} countries in database. Skipping initial load.")

            stocks_count = Stock.objects.count()
            if stocks_count == 0:
                logger.info("No stocks found in database. Loading initial stocks data...")
                loader = PolygonStocksLoaderService()
                created_stocks = loader.load_stocks_for_selected_countries()
                logger.info(f"Successfully loaded {created_stocks} stocks")
            else:
                logger.info(f"Found {stocks_count} stocks in database. Skipping initial load.")



        except Exception as e:
            logger.error(f"Error during initial data load: {str(e)}")