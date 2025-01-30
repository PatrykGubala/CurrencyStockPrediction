import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.services.currencies_data_service import CurrenciesDataService
import logging

from myapp.tasks import load_currency_data_task
logger = logging.getLogger(__name__)
@api_view(['GET'])
def get_all_currencies_data(request):
    service = CurrenciesDataService()
    try:
        data = service.get_all_data()
        return Response({"data": data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_all_currencies_data: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def load_currency_data(request):
    logger.info("Request received for loading currency data")
    try:
        data = request.data
        currency_ids = data.get('currency_ids', None)
        frequency = data.get('frequency', 'daily')
        logger.info(f"Loading data with frequency: {frequency}")
        task = load_currency_data_task.delay(currency_ids, frequency)
        logger.info("Data load initiated")
        return Response({"message": "Data load initiated", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(f"Error in load_currency_data: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_latest_currency_data(request, currency_id):
    service = CurrenciesDataService()
    try:
        latest_data = service.get_latest_data_for_currency(currency_id)
        if not latest_data:
            return Response({"error": "No data found for this currency"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"latest_data": latest_data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_latest_currency_data: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_percentage_change_for_currency(request, currency_id):
    service = CurrenciesDataService()
    try:
        change_data = service.get_percentage_change(currency_id)
        if not change_data:
            return Response({"error": "Unable to calculate percentage change"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"change_data": change_data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_percentage_change_for_currency: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='GET',
    operation_description="Retrieve currency data for currency code",
    manual_parameters=[
        openapi.Parameter(
            'currency_code',
            openapi.IN_PATH,
            description="Currency code (np. PLN)",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'frequency',
            openapi.IN_QUERY,
            description="Frequency (np. daily, hourly)",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'range',
            openapi.IN_QUERY,
            description="Range (np. last_month, all_data)",
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: "Currency data retrieved successfully.",
        404: "No data found for this currency.",
        500: "Internal server error."
    }
)
@api_view(['GET'])
def get_currency_data(request, currency_code):
    try:
        service = CurrenciesDataService()
        frequency = request.GET.get('frequency')
        range_param = request.GET.get('range')
        data = service.get_currency_data(currency_code, frequency, range_param)
        if data is None:
            return Response({"error": "No data found for this currency"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data": data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching currency data for {currency_code}: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_currency_percentage_changes(request, currency_code):
    service = CurrenciesDataService()
    changes = service.get_weekly_monthly_yearly_change(currency_code)
    if not changes:
        return Response({"error": "No data found for this currency"}, status=status.HTTP_404_NOT_FOUND)
    return Response(changes, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_monthly_percentage_change(request, currency_code):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    service = CurrenciesDataService()
    try:
        change_data = service.get_monthly_change(currency_code)
        if not change_data:
            return Response({"error": "Unable to calculate monthly change"}, status=status.HTTP_404_NOT_FOUND)
        return Response(change_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_monthly_percentage_change for {currency_code}: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)