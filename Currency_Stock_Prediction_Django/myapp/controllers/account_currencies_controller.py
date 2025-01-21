from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.services.account_currencies_service import AccountCurrenciesService
from myapp.utils.auth_utils import token_required




@api_view(['POST'])
@token_required
def add_currency_to_account(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        currency_code = data.get('currency_code')
        balance = data.get('balance', 0.0)
        if not currency_code:
            return Response({"error": "currency_code is required"}, status=status.HTTP_400_BAD_REQUEST)
        service = AccountCurrenciesService()
        account = request.current_user.account
        account_currency = service.add_currency_to_account(account.id, currency_code, balance)
        return Response({
            "message": "Currency added to account",
            "account_currency": account_currency
        }, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error adding currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@token_required
def get_account_currencies(request):
    service = AccountCurrenciesService()
    account = request.current_user.account
    currencies = service.get_account_currencies(account.id)
    return Response({"currencies": currencies}, status=status.HTTP_200_OK)


@api_view(['GET'])
@token_required
def get_account_currency_balance(request, currency_code):
    service = AccountCurrenciesService()
    account = request.current_user.account
    try:
        balance_info = service.get_single_account_currency_balance(account.id, currency_code)
        return Response(balance_info, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error retrieving balance", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@token_required
def update_account_currency_balance(request, currency_code):
    if request.method != 'PUT':
        return Response({"error": "Only PUT allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        balance = data.get('balance')
        if balance is None:
            return Response({"error": "balance is required"}, status=status.HTTP_400_BAD_REQUEST)
        service = AccountCurrenciesService()
        account = request.current_user.account
        account_currency = service.update_balance(account.id, currency_code, balance)
        return Response({"message": "Balance updated", "account_currency": account_currency}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error updating balance", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@token_required
def remove_currency_from_account(request, currency_code):
    if request.method != 'DELETE':
        return Response({"error": "Only DELETE allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        service = AccountCurrenciesService()
        account = request.current_user.account
        service.remove_currency_from_account(account.id, currency_code)
        return Response({"message": "Currency removed from account"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error removing currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def deposit_currency(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        amount = data.get('amount')
        if amount is None:
            return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = round(float(amount), 8)
            if amount <= 0:
                return Response({"error": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid amount. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        service = AccountCurrenciesService()
        account = request.current_user.account
        deposit_result = service.deposit_to_usd_account(account.id, amount)
        if deposit_result:
            return Response({
                "message": "Deposit successful.",
                "currency_code": deposit_result["currency_code"],
                "new_balance": deposit_result["new_balance"]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Deposit failed."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": "Error processing deposit.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@token_required
def buy_currency(request):
    if request.method != 'POST':
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        currency_code = data.get("currency_code")
        amount = float(data.get("amount", 0))
        if not currency_code:
            return Response({"error": "currency_code is required"}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"error": "Amount must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        service = AccountCurrenciesService()
        account = request.current_user.account
        service.buy_currency(account.id, currency_code, amount)
        return Response({"message": "Currency purchased successfully"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error buying currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@token_required
def sell_currency(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        currency_code = data.get("currency_code")
        amount = float(data.get("amount", 0))
        if not currency_code:
            return Response({"error": "currency_code is required"}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"error": "Amount must be > 0"}, status=status.HTTP_400_BAD_REQUEST)
        if not currency_code:
            return Response({"error": "currency_code is required"}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"error": "Amount must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        service = AccountCurrenciesService()
        account = request.current_user.account
        service.sell_currency(account.id, currency_code, amount)
        return Response({"message": "Currency sold successfully"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error selling currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def send_currency(request):
    try:
        data = request.data
        public_account_id = data.get('public_account_id')
        amount = data.get('amount')

        if not public_account_id or amount is None:
            return Response(
                {"error": "public_account_id and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = AccountCurrenciesService()
        sender_account_id = request.current_user.account.id
        send_result = service.send_currency(sender_account_id, public_account_id, amount)

        return Response(send_result, status=status.HTTP_200_OK)

    except ValueError as ve:
        return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error processing send currency.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )