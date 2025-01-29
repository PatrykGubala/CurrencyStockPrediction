from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)

class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):

        from myapp.signals import load_initial_data_after_migrate
        post_migrate.connect(load_initial_data_after_migrate, sender=self)




