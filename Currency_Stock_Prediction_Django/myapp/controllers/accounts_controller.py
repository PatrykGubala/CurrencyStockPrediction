from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.apps import logger
from myapp.services.account_currencies_service import AccountCurrenciesService
from myapp.services.accounts_service import AccountsService
from myapp.utils.auth_utils import token_required


@api_view(['GET'])
@token_required
def get_account_id(request):

    if request.method != 'GET':
        return Response({"error": "Only GET method is allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        service = AccountsService()
        account = request.current_user.account
        if account:
            return Response({"account_id": account.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Account not found for the user."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving account ID: {e}")
        return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_account(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
    except:
        return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

    user_id = data.get('user_id')
    account_name = data.get('account_name')
    currency_code = data.get('currency_code')

    accounts_service = AccountsService()
    try:
        account_dto = accounts_service.create_account(user_id, account_name, currency_code)
        return Response({"message": "Account created successfully", "account": account_dto}, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Failed to create account", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def recount_currency_values_test(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        service = AccountsService()
        logger.info("Starting recount_currency_values")
        service.recount_currency_values()
        logger.info("Finished recount_currency_values")
        return Response({"message": "Currency values have been recounted for testing."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed to recount currency values: {e}")
        return Response({"error": "Failed to recount currency values", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@token_required
def get_account_usd_value(request):
    if request.method == 'GET':
        service = AccountsService()
        account = request.current_user.account
        usd_balance = service.get_usd_balance(account.id)
        return Response({"usd_balance": float(usd_balance)}, status=status.HTTP_200_OK)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





@api_view(['GET'])
@token_required
def get_account_transactions(request):
    if request.method == 'GET':
        service = AccountsService()
        account = request.current_user.account

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        transactions_data = service.get_account_transactions(account.id, page, page_size)
        return Response(transactions_data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)