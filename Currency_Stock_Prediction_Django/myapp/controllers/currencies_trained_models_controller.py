from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from myapp.services.currencies_trained_models_service import CurrenciesTrainedModelsService
from myapp.models import Currency, CurrenciesPrediction
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository
from myapp.tasks import train_usdpln_model_async

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
    method='POST',
    operation_description="Train new USDPLN model asynchronously.",
    responses={200: "Training initiated", 400: "Bad Request"}
)
@api_view(['POST'])
def train_usdpln_model(request):
    result = train_usdpln_model_async.delay()
    return Response({"task_id": result.id}, status=status.HTTP_200_OK)


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