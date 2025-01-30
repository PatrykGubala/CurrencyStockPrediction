import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)

class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        if "test" not in sys.argv:
            from myapp.signals import load_initial_data_after_migrate
            post_migrate.connect(load_initial_data_after_migrate, sender=self)
        else:
            logger.info("TESTING")




