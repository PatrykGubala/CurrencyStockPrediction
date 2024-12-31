import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re

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


def validate_email(self: str) -> bool:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, self) is not None


@csrf_exempt
@token_required
def initiate_change_email(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        new_email = data.get('new_email')
        if not new_email:
            return JsonResponse({'error': 'New email is required'}, status=400)
        if not validate_email(new_email):
            return JsonResponse({'error': 'Invalid email format'}, status=400)

        users_service = UsersService()
        users_service.initiate_change_email(request.current_user, new_email)

        return JsonResponse({'message': 'Verification email sent. Please check your new email to verify the change.'}, status=200)
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to initiate email change', 'details': str(e)}, status=500)

@csrf_exempt
def verify_change_email(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET allowed'}, status=405)

    token = request.GET.get('token')
    if not token:
        return JsonResponse({'error': 'Invalid or missing token'}, status=400)

    users_service = UsersService()
    try:
        new_email = users_service.verify_change_email(token)
        return JsonResponse({
            'message': 'Email updated successfully.',
            'new_email': new_email
        }, status=200)
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to verify email change', 'details': str(e)}, status=500)





@csrf_exempt
@token_required
def change_username(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    new_username = data.get('new_username')

    if not new_username:
        return JsonResponse({'error': 'New username is required'}, status=400)

    users_service = UsersService()

    try:
        users_service.change_username(request.current_user, new_username)
        return JsonResponse({'message': 'Username changed successfully'}, status=200)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to change username', 'details': str(e)}, status=500)