from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from myapp.services.stocks_service import StocksService


@swagger_auto_schema(
    method='GET',
    operation_description="Get all stocks",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'stocks': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'symbol': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'company_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'exchange_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'share_class': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['GET'])
def get_all_stocks(request):
    stocks_service = StocksService()
    data = stocks_service.get_all_stocks_dto()
    return Response({"stocks": data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description="Add stock",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'stock_name': openapi.Schema(type=openapi.TYPE_STRING),
            'company_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'exchange_name': openapi.Schema(type=openapi.TYPE_STRING),
            'share_class': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'symbol': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'exchange_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'share_class': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['POST'])
def add_stock(request):
    stocks_service = StocksService()
    stock_symbol = request.data.get('stock_symbol')
    stock_name = request.data.get('stock_name')
    company_symbol = request.data.get('company_symbol')
    exchange_name = request.data.get('exchange_name')
    share_class = request.data.get('share_class')
    if not stock_symbol or not stock_name or not company_symbol:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    result = stocks_service.add_stock(stock_symbol, stock_name, company_symbol, exchange_name, share_class)
    return Response(result, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='PUT',
    operation_description="Update stock",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'stock_name': openapi.Schema(type=openapi.TYPE_STRING),
            'share_class': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'symbol': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'exchange_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'share_class': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        404: "Not found"
    }
)
@api_view(['PUT'])
def update_stock(request, stock_id: int):
    stocks_service = StocksService()
    stock_name = request.data.get('stock_name')
    share_class = request.data.get('share_class')
    updated = stocks_service.update_stock(stock_id, stock_name, share_class)
    if not updated:
        return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(updated, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='DELETE',
    operation_description="Delete a stock by ID",
    responses={
        200: "Success",
        404: "Not found"
    }
)
@api_view(['DELETE'])
def delete_stock(request, stock_id: int):
    stocks_service = StocksService()
    deleted = stocks_service.delete_stock(stock_id)
    if not deleted:
        return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "Stock deleted successfully"}, status=status.HTTP_200_OK)




