import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from myapp.apps import logger
from myapp.services.accounts_service import AccountsService

@csrf_exempt
def create_account(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_id = data.get('user_id')
    account_name = data.get('account_name')
    currency_code = data.get('currency_code')

    accounts_service = AccountsService()
    try:
        account_dto = accounts_service.create_account(user_id, account_name, currency_code)
        return JsonResponse({"message": "Account created successfully", "account": account_dto}, status=201)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to create account', 'details': str(e)}, status=500)


@csrf_exempt
def recount_currency_values_test(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        service = AccountsService()
        logger.info("Starting recount_currency_values")
        service.recount_currency_values()
        logger.info("Finished recount_currency_values")
        return JsonResponse({'message': 'Currency values have been recounted for testing.'}, status=200)
    except Exception as e:
        logger.error(f"Failed to recount currency values: {e}")
        return JsonResponse({'error': 'Failed to recount currency values', 'details': str(e)}, status=500)