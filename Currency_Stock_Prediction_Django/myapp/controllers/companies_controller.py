from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from myapp.services.companies_service import CompaniesService

@swagger_auto_schema(
    method='GET',
    operation_description="Get all companies",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'companies': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'symbol': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'logo_url': openapi.Schema(type=openapi.TYPE_STRING),
                            'country_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            }
        )
    }
)
@api_view(['GET'])
def get_all_companies(request):
    companies_service = CompaniesService()
    data = companies_service.get_all_companies()
    return Response({"companies": data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description="Create a new company",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company_symbol': openapi.Schema(type=openapi.TYPE_STRING),
            'company_name': openapi.Schema(type=openapi.TYPE_STRING),
            'logo_url': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'symbol': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'logo_url': openapi.Schema(type=openapi.TYPE_STRING),
                'country_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    }
)
@api_view(['POST'])
def create_company(request):
    companies_service = CompaniesService()
    symbol = request.data.get('company_symbol')
    name = request.data.get('company_name')
    logo_url = request.data.get('logo_url')
    if not symbol or not name:
        return Response({"error": "Company symbol and name are required."}, status=status.HTTP_400_BAD_REQUEST)
    company_created = companies_service.create_company(symbol, name, logo_url)
    return Response(company_created, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='DELETE',
    operation_description="Delete a company by ID",
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
def delete_company(request, company_id: int):
    companies_service = CompaniesService()
    deleted = companies_service.delete_company(company_id)
    if not deleted:
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "Company deleted successfully."}, status=status.HTTP_200_OK)
