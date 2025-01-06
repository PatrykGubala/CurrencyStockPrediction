from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from myapp.services.currencies_trained_models_service import CurrenciesTrainedModelsService
from myapp.models import Currency
from myapp.tasks import train_model_async
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository

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
    operation_description="Train new models for all currencies with data availability.",
    responses={200: "OK"}
)
@api_view(['POST'])
def train_new_models_for_all_currencies(request):
    task = train_model_async.delay()
    return Response({"message": "All-currency training task started", "task_id": task.id}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_description="List all trained models for a given currency",
    manual_parameters=[
        openapi.Parameter('currency_code', openapi.IN_QUERY, type=openapi.TYPE_STRING)
    ],
    responses={200: "OK", 404: "Not found"}
)
@api_view(['GET'])
def list_currency_models(request):
    currency_code = request.query_params.get('currency_code')
    if not currency_code:
        return Response({"error": "currency_code missing"}, status=status.HTTP_400_BAD_REQUEST)
    currency = Currency.objects.filter(code=currency_code).first()
    if not currency:
        return Response({"error": "Currency not found."}, status=status.HTTP_404_NOT_FOUND)
    repo = CurrenciesTrainedModelsRepository()
    models_list = repo.list_models_for_currency(currency)
    data = []
    for m in models_list:
        data.append({
            "model_id": m.id,
            "model_name": m.model_name,
            "training_date": m.training_date,
            "is_latest": m.is_latest,
            "metrics": m.metrics,
            "param_grid": m.param_grid
        })
    return Response(data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_description="List predictions for a given trained model",
    manual_parameters=[
        openapi.Parameter('model_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    ],
    responses={200: "OK", 404: "Not found"}
)
@api_view(['GET'])
def list_model_predictions(request):
    model_id = request.query_params.get('model_id')
    if not model_id:
        return Response({"error": "model_id missing"}, status=status.HTTP_400_BAD_REQUEST)
    repo = CurrenciesTrainedModelsRepository()
    trained_model = repo.get_trained_model_by_id(int(model_id))
    if not trained_model:
        return Response({"error": "Trained model not found"}, status=status.HTTP_404_NOT_FOUND)
    predictions = repo.list_predictions_for_model(trained_model)
    data = []
    for p in predictions:
        data.append({
            "id": p.id,
            "currency": p.currency.code,
            "prediction_date": p.prediction_date,
            "predicted_value": float(p.predicted_value)
        })
    return Response(data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description="Predict new data with existing model.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'model_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'days_ahead': openapi.Schema(type=openapi.TYPE_INTEGER, default=30)
        },
        required=['model_id']
    ),
    responses={200: "OK", 400: "Bad Request"}
)
@api_view(['POST'])
def predict_with_existing_model(request):
    service = CurrenciesTrainedModelsService()
    model_id = request.data.get('model_id')
    days_ahead = int(request.data.get('days_ahead', 30))
    if not model_id:
        return Response({"error": "model_id required"}, status=status.HTTP_400_BAD_REQUEST)
    result = service.predict_with_existing_model(model_id, days_ahead)
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)

