from typing import Optional, List
from django.db import transaction
from myapp.models import Currency, CurrenciesTrainedModels, CurrenciesPrediction
from decimal import Decimal, ROUND_HALF_UP, DecimalException

class CurrenciesTrainedModelsRepository:
    def create_trained_model(self, currency: Currency, model_name: str, model_file_path: str, metrics: dict, param_grid: dict, is_latest: bool = False) -> CurrenciesTrainedModels:
        trained_model = CurrenciesTrainedModels.objects.create(
            currency=currency,
            model_name=model_name,
            model_file_path=model_file_path,
            metrics=metrics,
            param_grid=param_grid,
            is_latest=is_latest
        )
        return trained_model

    def set_latest_model(self, currency: Currency, trained_model: CurrenciesTrainedModels):
        with transaction.atomic():
            CurrenciesTrainedModels.objects.filter(currency=currency).update(is_latest=False)
            trained_model.is_latest = True
            trained_model.save()

    def get_latest_model_for_currency(self, currency: Currency) -> Optional[CurrenciesTrainedModels]:
        return CurrenciesTrainedModels.objects.filter(currency=currency, is_latest=True).first()

    def add_predictions_bulk(self, currency: Currency, predictions: List[dict]) -> None:
        existing_dates = set(
            CurrenciesPrediction.objects.filter(
                currency=currency
            ).values_list('prediction_date', flat=True)
        )
        objects_to_create = []
        for item in predictions:
            if item['prediction_date'] in existing_dates:
                continue
            try:
                val = Decimal(str(item['predicted_value'])).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                max_value = Decimal('999999999.99999999')
                min_value = Decimal('-999999999.99999999')
                if val > max_value:
                    val = max_value
                elif val < min_value:
                    val = min_value
                obj = CurrenciesPrediction(
                    currency=currency,
                    predicted_value=val,
                    prediction_date=item['prediction_date']
                )
                objects_to_create.append(obj)
            except (ValueError, DecimalException):
                continue
        if objects_to_create:
            CurrenciesPrediction.objects.bulk_create(objects_to_create)

    def get_trained_model_by_id(self, model_id: int) -> Optional[CurrenciesTrainedModels]:
        return CurrenciesTrainedModels.objects.filter(id=model_id).first()

    def list_models_for_currency(self, currency: Currency) -> List[CurrenciesTrainedModels]:
        return list(CurrenciesTrainedModels.objects.filter(currency=currency).order_by('-training_date'))

    def list_predictions(self) -> List[CurrenciesPrediction]:
        return list(CurrenciesPrediction.objects.filter().order_by('prediction_date'))
