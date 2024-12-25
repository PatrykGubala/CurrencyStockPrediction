import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.account_currencies_service import AccountCurrenciesService
from myapp.utils.auth_utils import token_required




@csrf_exempt
@token_required
def add_currency_to_account(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        currency_code = data.get('currency_code')
        balance = data.get('balance', 0.0)
        if not currency_code:
            return JsonResponse({'error': 'currency_code is required'}, status=400)
        service = AccountCurrenciesService()
        account = request.current_user.account
        account_currency = service.add_currency_to_account(account.id, currency_code, balance)
        return JsonResponse({'message': 'Currency added to account', 'account_currency': account_currency}, status=201)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error adding currency', 'details': str(e)}, status=500)

@token_required
def get_account_currencies(request):
    service = AccountCurrenciesService()
    account = request.current_user.account
    currencies = service.get_account_currencies(account.id)
    return JsonResponse({'currencies': currencies}, status=200)

@csrf_exempt
@token_required
def update_account_currency_balance(request, currency_code):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Only PUT allowed'}, status=405)
    try:
        data = json.loads(request.body)
        balance = data.get('balance')
        if balance is None:
            return JsonResponse({'error': 'balance is required'}, status=400)
        service = AccountCurrenciesService()
        account = request.current_user.account
        account_currency = service.update_balance(account.id, currency_code, balance)
        return JsonResponse({'message': 'Balance updated', 'account_currency': account_currency}, status=200)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error updating balance', 'details': str(e)}, status=500)

@csrf_exempt
@token_required
def remove_currency_from_account(request, currency_code):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
    try:
        service = AccountCurrenciesService()
        account = request.current_user.account
        service.remove_currency_from_account(account.id, currency_code)
        return JsonResponse({'message': 'Currency removed from account'}, status=200)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error removing currency', 'details': str(e)}, status=500)



@csrf_exempt
@token_required
def deposit_currency(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        if amount is None:
            return JsonResponse({'error': 'Amount is required.'}, status=400)
        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount. Must be a number.'}, status=400)
        service = AccountCurrenciesService()
        account = request.current_user.account
        deposit_result = service.deposit_to_usd_account(account.id, amount)
        if deposit_result:
            return JsonResponse({
                'message': 'Deposit successful.',
                'currency_code': deposit_result['currency_code'],
                'new_balance': deposit_result['new_balance']
            }, status=200)
        else:
            return JsonResponse({'error': 'Deposit failed.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error processing deposit.', 'details': str(e)}, status=500)