from decimal import Decimal

from myapp.models import CurrenciesTrainedModels, CurrenciesPrediction, Currency, StocksTrainedModels, StocksPrediction, \
    Stock
from django.utils import timezone

class StocksTrainedModelsRepository:
    def create_trained_model(self, stock, model_name, model_file_path, metrics, param_grid, is_latest):
        if is_latest:
            StocksTrainedModels.objects.filter(stock=stock, is_latest=True).update(is_latest=False)

        trained_model = StocksTrainedModels(
            stock=stock,
            model_name=model_name,
            model_file_path=model_file_path,
            metrics=metrics,
            param_grid=param_grid,
            is_latest=is_latest
        )
        trained_model.save()
        return trained_model

    def clear_old_predictions(self, stock):
        StocksPrediction.objects.filter(stock=stock).delete()

    def store_predictions(self, stock, predictions):
        for index, value in predictions:
            try:
                predicted_value = Decimal(str(value))
            except Exception:
                predicted_value = None
            StocksPrediction.objects.create(
                stock=stock,
                predicted_value=predicted_value,
                prediction_date=index,
                created_at=timezone.now()
            )

    def mark_all_as_not_latest(self, stock):
        StocksTrainedModels.objects.filter(stock=stock, is_latest=True).update(is_latest=False)

    def get_stock_by_symbol(self, symbol):
        return Stock.objects.filter(stock_symbol__iexact=symbol).first()

    def get_latest_model(self, stock):
        return StocksTrainedModels.objects.filter(stock=stock, is_latest=True).first()
