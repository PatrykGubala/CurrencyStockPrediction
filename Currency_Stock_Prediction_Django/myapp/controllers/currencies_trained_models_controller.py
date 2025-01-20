from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from myapp.services.currencies_trained_models_service import CurrenciesTrainedModelsService
from myapp.models import Currency, CurrenciesPrediction
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository
from myapp.tasks import train_currency_model_async
@swagger_auto_schema(
    method='POST',
    operation_description="Train a new model for a given currency and store predictions.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'currency_code': openapi.Schema(type=openapi.TYPE_STRING),
            'model_name': openapi.Schema(type=openapi.TYPE_STRING, default="SeasonalRNN"),
            'future_days': openapi.Schema(type=openapi.TYPE_INTEGER, default=90)
        },
        required=['currency_code']
    ),
    responses={200: "OK", 400: "Bad Request"}
)
@api_view(['POST'])
def train_new_currency_model(request):
    service = CurrenciesTrainedModelsService()
    currency_code = request.data.get('currency_code')
    model_name = request.data.get('model_name', "SeasonalRNN")
    future_days = int(request.data.get('future_days', 90))
    result = service.train_model_for_currency(
        currency_code=currency_code,
        model_name=model_name,
        future_days=future_days,
        is_latest=True
    )
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)







@swagger_auto_schema(
    method='GET',
    operation_description="Get predictions for a given currency.",
    responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'predictions': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                        'predicted_value': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )}
)
@api_view(['GET'])
def get_currency_predictions(request, currency_code):
    try:
        currency = Currency.objects.get(code=currency_code)
    except Currency.DoesNotExist:
        return Response({"error": "Currency not found"}, status=status.HTTP_404_NOT_FOUND)
    predictions = CurrenciesPrediction.objects.filter(currency=currency).order_by('prediction_date')
    data = [{
        "timestamp": int(p.prediction_date.timestamp() * 1000),
        "predicted_value": str(p.predicted_value)
    } for p in predictions]
    return Response({"predictions": data}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description="Start asynchronous training of a currency model",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'currency_code': openapi.Schema(type=openapi.TYPE_STRING),
            'param_grid': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                default={
                    'rnn_type': ['LSTM'],
                    'n_layers': [1],
                    'units': [50],
                    'activation': ['relu'],
                    'optimizer': ['adam'],
                    'batch_size': [32],
                    'epochs': [50]
                }
            ),
            'sequence_length': openapi.Schema(type=openapi.TYPE_INTEGER, default=14),
            'dataset_time': openapi.Schema(type=openapi.TYPE_INTEGER, default=6),
            'prediction_time': openapi.Schema(type=openapi.TYPE_INTEGER, default=90),
            'short_term_lag': openapi.Schema(type=openapi.TYPE_INTEGER, default=7),
            'long_term_lag': openapi.Schema(type=openapi.TYPE_INTEGER, default=30),
            'scaling_method': openapi.Schema(type=openapi.TYPE_STRING, default='standard'),
            'output_directory': openapi.Schema(type=openapi.TYPE_STRING, default='forecasting_outputs'),
        },
        required=['currency_code']
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING),
                "task_id": openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        400: "Bad Request"
    }
)
@api_view(['POST'])
def start_async_currency_training(request):
    currency_code = request.data.get('currency_code')
    if not currency_code:
        return Response({"error": "Missing currency_code"}, status=status.HTTP_400_BAD_REQUEST)
    param_grid = request.data.get('param_grid', {
        'rnn_type': ['LSTM'],
        'n_layers': [1],
        'units': [50],
        'activation': ['relu'],
        'optimizer': ['adam'],
        'batch_size': [32],
        'epochs': [50]
    })
    sequence_length = int(request.data.get('sequence_length', 14))
    dataset_time = int(request.data.get('dataset_time', 6))
    prediction_time = int(request.data.get('prediction_time', 90))
    short_term_lag = int(request.data.get('short_term_lag', 7))
    long_term_lag = int(request.data.get('long_term_lag', 30))
    scaling_method = request.data.get('scaling_method', 'standard')
    output_directory = request.data.get('output_directory', 'forecasting_outputs')
    task = train_currency_model_async.delay(
        currency_code,
        param_grid,
        sequence_length,
        dataset_time,
        prediction_time,
        short_term_lag,
        long_term_lag,
        scaling_method,
        output_directory
    )
    return Response({"message":"Training task started","task_id":task.id}, status=status.HTTP_200_OK)
