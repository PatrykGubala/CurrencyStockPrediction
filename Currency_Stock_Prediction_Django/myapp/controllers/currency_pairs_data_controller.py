import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.currency_pairs_data_service import CurrencyPairsDataService
import logging

from myapp.tasks import load_currency_data_task
logger = logging.getLogger(__name__)
def get_all_currency_pair_data(request):
    service = CurrencyPairsDataService()
    data = service.get_all_data()
    return JsonResponse({"data": data}, status=200)

@csrf_exempt
def load_currency_pair_data(request):
    logger.info("Request received for loading currency pair data")
    if request.method != 'POST':
        logger.warning("Invalid request method for loading data")
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    data = json.loads(request.body)
    pair_ids = data.get('pair_ids', None)
    frequency = data.get('frequency', 'daily')
    logger.info(f"Loading data with frequency: {frequency}")
    task = load_currency_data_task.delay(pair_ids, frequency)
    logger.info("Data load completed")
    return JsonResponse({"message": "Data load initiated.", "task_id": task.id}, status=202)


def get_latest_currency_pair_data(request, pair_id):
    service = CurrencyPairsDataService()
    latest_data = service.get_latest_data_for_pair(pair_id)
    if not latest_data:
        return JsonResponse({"error": "No data found for this pair."}, status=404)
    return JsonResponse({"latest_data": latest_data}, status=200)

def get_percentage_change_for_pair(request, pair_id):
    service = CurrencyPairsDataService()
    change_data = service.get_percentage_change(pair_id)
    if not change_data:
        return JsonResponse({"error": "Unable to calculate percentage change."}, status=404)
    return JsonResponse({"change_data": change_data}, status=200)