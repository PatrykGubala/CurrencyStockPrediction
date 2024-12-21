import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.currencies_data_service import CurrenciesDataService
import logging

from myapp.tasks import load_currency_data_task
logger = logging.getLogger(__name__)
def get_all_currencies_data(request):
    service = CurrenciesDataService()
    data = service.get_all_data()
    return JsonResponse({"data": data}, status=200)

@csrf_exempt
def load_currency_data(request):
    logger.info("Request received for loading currency data")
    if request.method != 'POST':
        logger.warning("Invalid request method for loading data")
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    data = json.loads(request.body)
    currency_ids = data.get('currency_ids', None)
    frequency = data.get('frequency', 'daily')
    logger.info(f"Loading data with frequency: {frequency}")
    task = load_currency_data_task.delay(currency_ids, frequency)
    logger.info("Data load completed")
    return JsonResponse({"message": "Data load initiated.", "task_id": task.id}, status=202)


def get_latest_currency_data(request, currency_id):
    service = CurrenciesDataService()
    latest_data = service.get_latest_data_for_currency(currency_id)
    if not latest_data:
        return JsonResponse({"error": "No data found for this currency."}, status=404)
    return JsonResponse({"latest_data": latest_data}, status=200)

def get_percentage_change_for_currency(request, currency_id):
    service = CurrenciesDataService()
    change_data = service.get_percentage_change(currency_id)
    if not change_data:
        return JsonResponse({"error": "Unable to calculate percentage change."}, status=404)
    return JsonResponse({"change_data": change_data}, status=200)



