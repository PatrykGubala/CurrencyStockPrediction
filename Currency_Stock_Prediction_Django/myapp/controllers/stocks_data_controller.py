from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.apps import logger
from myapp.services.stocks_data_service import StocksDataService
from myapp.tasks import load_stocks_data_task


@swagger_auto_schema(method='POST',operation_description="Load daily data for a stock symbol",request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),'start_date': openapi.Schema(type=openapi.TYPE_STRING),'end_date': openapi.Schema(type=openapi.TYPE_STRING)}),responses={202:"Data load initiated"})
@api_view(['POST'])
def load_daily_stock_data(request):
    data = request.data
    symbol = data.get('stock_symbol')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    stocks_data_service = StocksDataService()
    stocks_data_service.load_daily_data_for_range(symbol, start_date, end_date)
    return Response({"message": "Data load initiated."}, status=status.HTTP_202_ACCEPTED)

@swagger_auto_schema(method='POST',operation_description="Load hourly data for a stock symbol",request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),'start_date': openapi.Schema(type=openapi.TYPE_STRING),'end_date': openapi.Schema(type=openapi.TYPE_STRING)}),responses={202:"Data load initiated"})
@api_view(['POST'])
def load_hourly_stock_data(request):
    data = request.data
    symbol = data.get('stock_symbol')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    stocks_data_service = StocksDataService()
    stocks_data_service.load_hourly_data_for_range(symbol, start_date, end_date)
    return Response({"message": "Data load initiated."}, status=status.HTTP_202_ACCEPTED)




@api_view(['POST'])
def load_stock_data(request):
    logger.info("Request received for loading stock data")
    try:
        data = request.data
        stock_ids = data.get('stock_ids', None)
        frequency = data.get('frequency', 'daily')
        logger.info(f"Loading data with frequency: {frequency}")
        task = load_stocks_data_task.delay(stock_ids, frequency)
        logger.info("Data load initiated")
        return Response({"message": "Data load initiated.", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(f"Error in load_stock_data: {e}")
        return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@swagger_auto_schema(method='GET',operation_description="Get all stored stock data",responses={200: openapi.Schema(type=openapi.TYPE_OBJECT,properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY,items=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),'timestamp': openapi.Schema(type=openapi.TYPE_STRING),'open_price': openapi.Schema(type=openapi.TYPE_STRING),'high_price': openapi.Schema(type=openapi.TYPE_STRING),'low_price': openapi.Schema(type=openapi.TYPE_STRING),'close_price': openapi.Schema(type=openapi.TYPE_STRING),'volume': openapi.Schema(type=openapi.TYPE_STRING)}))})})
@api_view(['GET'])
def get_all_stocks_data(request):
    stocks_data_service = StocksDataService()
    data = stocks_data_service.get_all_data()
    return Response({"data": data}, status=status.HTTP_200_OK)

@swagger_auto_schema(method='GET',operation_description="Get the latest stock data for a specific symbol",responses={200: openapi.Schema(type=openapi.TYPE_OBJECT,properties={'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),'timestamp': openapi.Schema(type=openapi.TYPE_STRING),'open_price': openapi.Schema(type=openapi.TYPE_STRING),'high_price': openapi.Schema(type=openapi.TYPE_STRING),'low_price': openapi.Schema(type=openapi.TYPE_STRING),'close_price': openapi.Schema(type=openapi.TYPE_STRING),'volume': openapi.Schema(type=openapi.TYPE_STRING)}),404:"Not found"})
@api_view(['GET'])
def get_latest_stock_data(request, stock_symbol):
    stocks_data_service = StocksDataService()
    latest = stocks_data_service.get_latest_data_for_stock(stock_symbol)
    if not latest:
        return Response({"error": "No data found for this stock."}, status=status.HTTP_404_NOT_FOUND)
    return Response(latest, status=status.HTTP_200_OK)

@swagger_auto_schema(method='GET',operation_description="Get aggregated stock data",manual_parameters=[openapi.Parameter('frequency', openapi.IN_QUERY, description="daily or hourly", type=openapi.TYPE_STRING),openapi.Parameter('range', openapi.IN_QUERY, description="all_data or last_month", type=openapi.TYPE_STRING)],responses={200: openapi.Schema(type=openapi.TYPE_OBJECT,properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY,items=openapi.Schema(type=openapi.TYPE_OBJECT,properties={'timestamp': openapi.Schema(type=openapi.TYPE_STRING),'open_price': openapi.Schema(type=openapi.TYPE_STRING),'high_price': openapi.Schema(type=openapi.TYPE_STRING),'low_price': openapi.Schema(type=openapi.TYPE_STRING),'close_price': openapi.Schema(type=openapi.TYPE_STRING),'volume': openapi.Schema(type=openapi.TYPE_STRING)}))}),404:"Not found"})
@api_view(['GET'])
def get_stock_data(request, stock_symbol):
    frequency = request.GET.get('frequency', 'daily')
    range_param = request.GET.get('range', 'last_month')
    stocks_data_service = StocksDataService()
    data = stocks_data_service.get_stock_data(stock_symbol, frequency, range_param)
    if data is None:
        return Response({"error": "No data found for this stock."}, status=status.HTTP_404_NOT_FOUND)
    return Response({"data": data}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='GET',
    operation_description="Get monthly percentage change for a specific stock symbol.",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'stock_symbol': openapi.Schema(type=openapi.TYPE_STRING),
                'monthly_change': openapi.Schema(type=openapi.TYPE_NUMBER)
            }
        ),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_stocks_monthly_percentage_change(request, stock_symbol):
    service = StocksDataService()
    monthly_change = service.get_monthly_change(stock_symbol)
    if not monthly_change:
        return Response({"error": "No monthly change data found for this stock."}, status=status.HTTP_404_NOT_FOUND)
    return Response(monthly_change, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description="Get weekly, monthly and yearly percentage changes for a specific stock symbol",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'weekly_change': openapi.Schema(type=openapi.TYPE_STRING),
                'monthly_change': openapi.Schema(type=openapi.TYPE_STRING),
                'yearly_change': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_weekly_monthly_yearly_change(request, stock_symbol):
    service = StocksDataService()
    changes = service.get_weekly_monthly_yearly_change(stock_symbol)
    if not changes:
        return Response({"error": "No data found for this stock."}, status=status.HTTP_404_NOT_FOUND)
    return Response(changes, status=status.HTTP_200_OK)