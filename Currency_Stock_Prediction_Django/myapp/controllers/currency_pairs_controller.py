import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.currency_pairs_service import CurrencyPairsService

@csrf_exempt
def create_currency_pair(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        base_currency_code = data.get('base_currency_code')
        target_currency_code = data.get('target_currency_code')
        if not base_currency_code or not target_currency_code:
            return JsonResponse({"error": "Both base_currency_code and target_currency_code are required."}, status=400)
        service = CurrencyPairsService()
        pair_dto = service.create_currency_pair(base_currency_code, target_currency_code)
        if not pair_dto:
            return JsonResponse({"error": "Failed to create currency pair. Check if currencies exist."}, status=400)
        return JsonResponse({"currency_pair": pair_dto}, status=201)
    except Exception as e:
        return JsonResponse({"error": "Error creating currency pair.", "details": str(e)}, status=500)

def get_all_currency_pairs(request):
    service = CurrencyPairsService()
    pairs = service.get_all_currency_pairs_dto()
    return JsonResponse({"currency_pairs": pairs}, status=200)

def get_currency_pair(request, pair_id):
    service = CurrencyPairsService()
    pair = service.get_currency_pair_by_id_dto(pair_id)
    if not pair:
        return JsonResponse({"error": "Currency pair not found."}, status=404)
    return JsonResponse({"currency_pair": pair}, status=200)

@csrf_exempt
def delete_currency_pair(request, pair_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
    service = CurrencyPairsService()
    result = service.delete_currency_pair(pair_id)
    if result:
        return JsonResponse({"message": "Currency pair deleted successfully."}, status=200)
    else:
        return JsonResponse({"error": "Currency pair not found."}, status=404)
