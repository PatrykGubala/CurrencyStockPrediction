from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myapp.services.stocks_recommendations_service import StockRecommendationsService

@swagger_auto_schema(
    method='POST',
    operation_description="Load and create stock recommendations for a given symbol from Finnhub",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'symbol': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recommendations': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),
                            'date': openapi.Schema(type=openapi.TYPE_STRING),
                            'buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'hold': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['POST'])
def create_stock_recommendations(request):
    symbol = request.data.get('symbol')
    if not symbol:
        return Response({"error": "Symbol is required"}, status=status.HTTP_400_BAD_REQUEST)
    recommendations_service = StockRecommendationsService()
    recommendations = recommendations_service.load_recommendations_for_symbol(symbol)
    if not recommendations:
        return Response({"error": f"No recommendations created for '{symbol}'."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"recommendations": recommendations}, status=status.HTTP_201_CREATED)



@swagger_auto_schema(
    method='POST',
    operation_description="Load and create stock recommendations for a given symbol from Finnhub",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recommendations': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),
                            'date': openapi.Schema(type=openapi.TYPE_STRING),
                            'buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'hold': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['POST'])
def load_stocks_recommendations(request):
    loader = StockRecommendationsService()
    recommendations_service = StockRecommendationsService()

    recommendations = recommendations_service.load_recommendations_for_all_stocks()
    return Response({"created_recommendations": recommendations},
            status=status.HTTP_201_CREATED
        )

@swagger_auto_schema(
    method='GET',
    operation_description="Retrieve all existing recommendations for a given symbol",
    manual_parameters=[
        openapi.Parameter('symbol', openapi.IN_QUERY, description="Stock symbol", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recommendations': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),
                            'date': openapi.Schema(type=openapi.TYPE_STRING),
                            'buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'hold': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_buy': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'strong_sell': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['GET'])
def get_stock_recommendations(request):
    symbol = request.GET.get('symbol')
    if not symbol:
        return Response({"error": "Symbol query param is required"}, status=status.HTTP_400_BAD_REQUEST)
    recommendations_service = StockRecommendationsService()
    recommendations = recommendations_service.get_recommendations_for_symbol(symbol)
    return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)
