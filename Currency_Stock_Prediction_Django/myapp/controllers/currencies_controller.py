import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.currencies_service import CurrenciesService

def get_all_currencies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_all_currencies_dto()
        return JsonResponse({"currencies": currencies_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching currencies", "details": str(e)}, status=500)

def get_currency_by_code(request, code):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currency_dto = service.get_currency_by_code_dto(code)
        if not currency_dto:
            return JsonResponse({"error": "Currency not found."}, status=404)
        return JsonResponse({"currency": currency_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching currency", "details": str(e)}, status=500)

@csrf_exempt
def add_currency(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        code = data.get('code')
        name = data.get('name')
        symbol = data.get('symbol')
        if not code or not name:
            return JsonResponse({"error": "Currency code and name are required."}, status=400)
        service = CurrenciesService()
        currency_dto = service.add_currency(code, name, symbol)
        return JsonResponse({"currency": currency_dto}, status=201)
    except Exception as e:
        return JsonResponse({"error": "Error adding currency", "details": str(e)}, status=500)

@csrf_exempt
def update_currency(request, currency_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Only PUT allowed'}, status=405)
    try:
        data = json.loads(request.body)
        new_name = data.get('name')
        new_symbol = data.get('symbol')
        if not new_name:
            return JsonResponse({"error": "New currency name is required."}, status=400)
        service = CurrenciesService()
        currency_dto = service.update_currency(currency_id, new_name, new_symbol)
        if not currency_dto:
            return JsonResponse({"error": "Currency not found."}, status=404)
        return JsonResponse({"currency": currency_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error updating currency", "details": str(e)}, status=500)

@csrf_exempt
def delete_currency(request, currency_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
    service = CurrenciesService()
    try:
        result = service.delete_currency(currency_id)
        if result:
            return JsonResponse({"message": "Currency deleted successfully."}, status=200)
        else:
            return JsonResponse({"error": "Currency not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Error deleting currency", "details": str(e)}, status=500)
def get_european_currencies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Europe')
        return JsonResponse({"currencies": currencies_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching European currencies", "details": str(e)}, status=500)

def get_asian_currencies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Asia')
        return JsonResponse({"currencies": currencies_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching Asian currencies", "details": str(e)}, status=500)

def get_american_currencies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Americas')
        return JsonResponse({"currencies": currencies_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching American currencies", "details": str(e)}, status=500)


def get_oceanian_currencies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Oceania')
        return JsonResponse({"currencies": currencies_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Error fetching Oceanian currencies", "details": str(e)}, status=500)


@csrf_exempt
def convert_currency(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        from_currency_code = data.get('from_currency')
        to_currency_code = data.get('to_currency')

        if amount is None or from_currency_code is None or to_currency_code is None:
            return JsonResponse({"error": "Missing required fields: amount, from_currency, to_currency."}, status=400)

        try:
            amount = float(amount)
            if amount <= 0:
                return JsonResponse({"error": "Amount must be a positive number."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid amount. Must be a number."}, status=400)

        service = CurrenciesService()
        converted_amount, rate = service.convert_currency(amount, from_currency_code, to_currency_code)

        if converted_amount is None:
            return JsonResponse({"error": "Conversion failed. Check currency codes and data availability."}, status=400)

        return JsonResponse({
            "converted_amount": converted_amount,
            "conversion_rate": rate
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Error converting currency.", "details": str(e)}, status=500)