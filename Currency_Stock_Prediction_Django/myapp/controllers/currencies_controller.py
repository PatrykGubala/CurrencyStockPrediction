import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapp.services.currencies_service import CurrenciesService

@api_view(['GET'])
def get_all_currencies(request):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_all_currencies_dto()
        return Response({"currencies": currencies_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching currencies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_currency_by_code(request, code):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currency_dto = service.get_currency_by_code_dto(code)
        if not currency_dto:
            return Response({"error": "Currency not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"currency": currency_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_currency(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        code = data.get('code')
        name = data.get('name')
        symbol = data.get('symbol')
        if not code or not name:
            return Response({"error": "Currency code and name are required."}, status=status.HTTP_400_BAD_REQUEST)
        service = CurrenciesService()
        currency_dto = service.add_currency(code, name, symbol)
        return Response({"currency": currency_dto}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": "Error adding currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_currency(request, currency_id):
    if request.method != 'PUT':
        return Response({"error": "Only PUT allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        new_name = data.get('name')
        new_symbol = data.get('symbol')
        if not new_name:
            return Response({"error": "New currency name is required."}, status=status.HTTP_400_BAD_REQUEST)
        service = CurrenciesService()
        currency_dto = service.update_currency(currency_id, new_name, new_symbol)
        if not currency_dto:
            return Response({"error": "Currency not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"currency": currency_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error updating currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['DELETE'])
def delete_currency(request, currency_id):
    if request.method != 'DELETE':
        return Response({"error": "Only DELETE allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        result = service.delete_currency(currency_id)
        if result:
            return Response({"message": "Currency deleted successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Currency not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Error deleting currency", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_european_currencies(request):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Europe')
        return Response({"currencies": currencies_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching European currencies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_asian_currencies(request):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Asia')
        return Response({"currencies": currencies_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching Asian currencies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_american_currencies(request):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Americas')
        return Response({"currencies": currencies_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching American currencies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_oceanian_currencies(request):
    if request.method != 'GET':
        return Response({"error": "Only GET allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    service = CurrenciesService()
    try:
        currencies_dto = service.get_currencies_by_region('Oceania')
        return Response({"currencies": currencies_dto}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error fetching Oceanian currencies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def convert_currency(request):
    if request.method != 'POST':
        return Response({"error": "Only POST allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        data = request.data
        amount = data.get('amount')
        from_currency_code = data.get('from_currency')
        to_currency_code = data.get('to_currency')

        if amount is None or from_currency_code is None or to_currency_code is None:
            return Response({"error": "Missing required fields: amount, from_currency, to_currency."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be a positive number."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid amount. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        service = CurrenciesService()
        converted_amount, rate = service.convert_currency(amount, from_currency_code, to_currency_code)

        if converted_amount is None:
            return Response({"error": "Conversion failed. Check currency codes and data availability."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "converted_amount": converted_amount,
            "conversion_rate": rate
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Error converting currency.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


