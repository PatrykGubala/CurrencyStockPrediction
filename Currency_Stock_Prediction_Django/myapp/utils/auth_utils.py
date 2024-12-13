from firebase_admin import auth
from django.http import JsonResponse
from functools import wraps
from myapp.services.users_service import UsersService


def token_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing'}, status=401)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return JsonResponse({'error': 'Invalid token format'}, status=401)

        id_token = parts[1]
        try:
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token.get('uid')
            if not firebase_uid:
                return JsonResponse({'error': 'Invalid token: UID missing'}, status=401)

            users_service = UsersService()
            user = users_service.get_user_by_firebase_uid(firebase_uid)
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            request.current_user = user
        except auth.ExpiredIdTokenError:
            return JsonResponse({'error': 'Token has expired'}, status=401)

        except auth.RevokedIdTokenError:
            return JsonResponse({'error': 'Token has been revoked'}, status=401)

        except auth.InvalidIdTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        except Exception as e:
            return JsonResponse({'error': 'Authentication failed', 'details': str(e)}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
