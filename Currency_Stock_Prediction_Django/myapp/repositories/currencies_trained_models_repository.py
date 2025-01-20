import os
from decimal import Decimal

from django.db.models import Q
from myapp.models import CurrenciesTrainedModels, CurrenciesPrediction, Currency
from django.utils import timezone

class CurrenciesTrainedModelsRepository:
    def create_trained_model(self, currency, model_name, model_file_path, metrics, param_grid, is_latest):
        trained_model = CurrenciesTrainedModels(
            currency=currency,
            model_name=model_name,
            model_file_path=model_file_path,
            metrics=metrics,
            param_grid=param_grid,
            is_latest=is_latest
        )
        trained_model.save()
        return trained_model

    def clear_old_predictions(self, currency):
        CurrenciesPrediction.objects.filter(currency=currency).delete()

    def store_predictions(self, currency, predictions):
        for index, value in predictions:
            try:
                predicted_value = Decimal(str(value))
            except Exception:
                predicted_value = None
            CurrenciesPrediction.objects.create(
                currency=currency,
                predicted_value=predicted_value,
                prediction_date=index,
                created_at=timezone.now()
            )

    def mark_all_as_not_latest(self, currency):
        CurrenciesTrainedModels.objects.filter(currency=currency).update(is_latest=False)

    def get_currency_by_code(self, code):
        return Currency.objects.filter(code=code).first()
