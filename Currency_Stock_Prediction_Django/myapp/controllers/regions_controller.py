import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.regions_service import RegionsService

def get_all_regions(request):
    service = RegionsService()
    try:
        regions_dto = service.get_all_regions_dto()
        return JsonResponse({"regions": regions_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas pobierania regionów.", "details": str(e)}, status=500)

def get_region(request, region_id):
    service = RegionsService()
    try:
        region_dto = service.get_region_by_id_dto(region_id)
        if not region_dto:
            return JsonResponse({"error": "Region not found."}, status=404)
        return JsonResponse({"region": region_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas pobierania regionu.", "details": str(e)}, status=500)

@csrf_exempt
def load_regions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        regions = data.get('regions')
        if not regions or not isinstance(regions, list):
            return JsonResponse({"error": "A list of regions is required."}, status=400)
        service = RegionsService()
        added_regions = []
        for rn in regions:
            r = service.add_region(rn)
            added_regions.append(r)
        return JsonResponse({"message": "Regions loaded successfully.", "regions": added_regions}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas ładowania regionów.", "details": str(e)}, status=500)

@csrf_exempt
def create_region(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        region_name = data.get('region_name')
        if not region_name:
            return JsonResponse({"error": "Region name is required."}, status=400)
        service = RegionsService()
        region_dto = service.add_region(region_name)
        return JsonResponse({"region": region_dto}, status=201)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas tworzenia regionu.", "details": str(e)}, status=500)

@csrf_exempt
def update_region(request, region_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Only PUT allowed'}, status=405)
    try:
        data = json.loads(request.body)
        new_name = data.get('region_name')
        if not new_name:
            return JsonResponse({"error": "New region name is required."}, status=400)
        service = RegionsService()
        region_dto = service.update_region(region_id, new_name)
        if not region_dto:
            return JsonResponse({"error": "Region not found."}, status=404)
        return JsonResponse({"region": region_dto}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas aktualizacji regionu.", "details": str(e)}, status=500)

@csrf_exempt
def delete_region(request, region_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
    try:
        service = RegionsService()
        result = service.delete_region(region_id)
        if result:
            return JsonResponse({"message": "Region deleted successfully."}, status=200)
        else:
            return JsonResponse({"error": "Region not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Wystąpił nieoczekiwany błąd podczas usuwania regionu.", "details": str(e)}, status=500)
