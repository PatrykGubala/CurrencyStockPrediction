from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.services.account_stocks_service import AccountStocksService
from myapp.utils.auth_utils import token_required

@api_view(['GET'])
@token_required
def get_account_stock_shares(request, stock_symbol):
    try:
        service = AccountStocksService()
        account = request.current_user.account
        balance_info = service.get_account_stock_balance(account.id, stock_symbol)
        return Response(balance_info, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Error retrieving shares", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@token_required
def get_stock_transactions(request):
    try:
        service = AccountStocksService()
        account = request.current_user.account
        transactions = service.get_transactions(account.id)
        return Response({"transactions": transactions}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error retrieving transactions", "details": str(e)},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@token_required
def buy_stock(request):
    try:
        data = request.data
        stock_symbol = data.get("stock_symbol")
        shares = float(data.get("shares", 0))
        if not stock_symbol:
            return Response({"error": "stock_symbol is required"}, status=status.HTTP_400_BAD_REQUEST)
        if shares <= 0:
            return Response({"error": "Shares amount must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        service = AccountStocksService()
        account = request.current_user.account
        service.buy_stock(account.id, stock_symbol, shares)
        return Response({"message": "Stock purchased successfully"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error buying stock", "details": str(e)},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@token_required
def sell_stock(request):
    try:
        data = request.data
        stock_symbol = data.get("stock_symbol")
        shares = float(data.get("shares", 0))
        if not stock_symbol:
            return Response({"error": "stock_symbol is required"}, status=status.HTTP_400_BAD_REQUEST)
        if shares <= 0:
            return Response({"error": "Shares amount must be > 0"}, status=status.HTTP_400_BAD_REQUEST)

        service = AccountStocksService()
        account = request.current_user.account
        service.sell_stock(account.id, stock_symbol, shares)
        return Response({"message": "Stock sold successfully"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Error selling stock", "details": str(e)},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)