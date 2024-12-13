import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.countries_service import CountriesService

@csrf_exempt
def load_only_countries(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    service = CountriesService()
    try:
        data = service.fetch_countries_data()
        service.load_only_countries(data)
        return JsonResponse({"message": "Tylko kraje zostały załadowane pomyślnie."}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd.", "details": str(e)}, status=500)

@csrf_exempt
def load_countries_with_details(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    service = CountriesService()
    try:
        service.load_all_data()
        return JsonResponse({"message": "Kraje wraz z regionami i walutami zostały załadowane pomyślnie."}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd.", "details": str(e)}, status=500)

def get_all_countries(request):
    service = CountriesService()
    try:
        countries_dto = service.get_all_countries_dto()
        return JsonResponse({"countries": countries_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas pobierania krajów.", "details": str(e)}, status=500)

def get_country(request, country_code):
    service = CountriesService()
    try:
        country_dto = service.get_country_by_code_dto(country_code.upper())
        if not country_dto:
            return JsonResponse({"error": "Kraj nie został znaleziony."}, status=404)
        return JsonResponse({"country": country_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas pobierania kraju.", "details": str(e)}, status=500)
