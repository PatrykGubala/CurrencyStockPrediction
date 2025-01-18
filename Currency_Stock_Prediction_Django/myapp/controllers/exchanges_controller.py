from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from myapp.services.exchanges_service import ExchangesService

@swagger_auto_schema(
    method='GET',
    operation_description="Get all exchanges",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exchanges': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'country_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['GET'])
def get_all_exchanges(request):
    exchanges_service = ExchangesService()
    data = exchanges_service.get_all_exchanges()
    return Response({"exchanges": data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description="Create a new exchange",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'country_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    }
)
@api_view(['POST'])
def create_exchange(request):
    exchanges_service = ExchangesService()
    exchange_name = request.data.get('name')
    if not exchange_name:
        return Response({"error": "Exchange name is required"}, status=status.HTTP_400_BAD_REQUEST)
    exchange = exchanges_service.create_exchange(exchange_name)
    return Response(exchange, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='DELETE',
    operation_description="Delete an exchange by ID",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        404: "Not found"
    }
)
@api_view(['DELETE'])
def delete_exchange(request, exchange_id: int):
    exchanges_service = ExchangesService()
    deleted = exchanges_service.delete_exchange(exchange_id)
    if not deleted:
        return Response({"error": "Exchange not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "Exchange deleted successfully."}, status=status.HTTP_200_OK)
