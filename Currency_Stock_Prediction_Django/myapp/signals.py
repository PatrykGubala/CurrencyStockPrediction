import logging
logger = logging.getLogger(__name__)

def load_initial_data_after_migrate(sender, **kwargs):
    try:
        from myapp.models import Country, Stock
        from myapp.tasks import load_initial_countries_data_task, load_initial_stocks_data_task

        countries_count = Country.objects.count()
        if countries_count <= 1:
            load_initial_countries_data_task.delay()

        stocks_count = Stock.objects.count()
        if stocks_count == 0:
            load_initial_stocks_data_task.delay()

    except Exception as e:
        logger.error(f"Error during initial data load: {str(e)}")
