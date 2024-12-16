import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.services.users_service import UsersService
from myapp.utils.auth_utils import token_required


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


@token_required
def get_user_info(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)

    user = request.current_user
    profile_image_url = None

    if user.profile_image_url:
        media_url = settings.MEDIA_URL
        relative_path = user.profile_image_url.replace('\\', '/')
        profile_image_url = request.build_absolute_uri(os.path.join(media_url, relative_path))

    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'profile_image_url': profile_image_url
    }, status=200)


@csrf_exempt
@token_required
def upload_profile_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body)
        image_base64 = data.get('image_base64')
        if not image_base64:
            return JsonResponse({'error': 'No image data provided'}, status=400)
        users_service = UsersService()
        relative_path = users_service.upload_profile_image(request.current_user, image_base64)
        full_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, relative_path))
        return JsonResponse({'profile_image_url': full_url}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to upload image', 'details': str(e)}, status=500)