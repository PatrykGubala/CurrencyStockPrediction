import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.users_service import UsersService

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    users_service = UsersService()

    try:
        users_service.register_user(data)
        return JsonResponse({'message': 'User registered successfully in database'}, status=201)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to register user in database', 'details': str(e)}, status=500)

def get_user_by_id(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)
    users_service = UsersService()
    try:
        user_dto = users_service.get_user_by_id_dto(user_id)
        if not user_dto:
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse(user_dto, status=200)
    except Exception as e:
        return JsonResponse({'error': 'Error retrieving user', 'details': str(e)}, status=500)
