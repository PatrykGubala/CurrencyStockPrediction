from django.http import JsonResponse
from rest_framework.decorators import api_view
from myapp.services.users_contacts_service import UsersContactsService
from myapp.apps import logger
from myapp.utils.auth_utils import token_required

@api_view(['POST'])
@token_required
def create_contact(request):
    user = request.current_user
    data = request.data

    title = data.get('title')
    public_account_id = data.get('public_account_id')
    account_name = data.get('account_name')

    if not all([title, public_account_id, account_name]):
        return JsonResponse(
            {'error': 'Missing required fields.'},
            status=400
        )

    service = UsersContactsService()

    try:
        contact = service.create_contact(
            user=user,
            title=title,
            public_account_id=public_account_id,
            account_name=account_name
        )
        contact_data = {
            'id': contact.id,
            'title': contact.title,
            'public_account_id': contact.public_account_id,
            'account_name': contact.account_name
        }
        return JsonResponse(
            {'message': 'Contact created successfully.', 'contact': contact_data},
            status=201
        )
    except ValueError as ve:
        logger.error(f"Validation error while creating contact: {ve}")
        return JsonResponse(
            {'error': str(ve)},
            status=400
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating contact: {e}")
        return JsonResponse(
            {'error': 'Failed to create contact.'},
            status=500
        )

@api_view(['GET'])
@token_required
def list_contacts(request):
    user = request.current_user
    service = UsersContactsService()

    try:
        contacts = service.list_contacts(user=user)
        contacts_data = [
            {
                'id': contact.id,
                'title': contact.title,
                'public_account_id': contact.public_account_id,
                'account_name': contact.account_name
            }
            for contact in contacts
        ]
        return JsonResponse(
            {'contacts': contacts_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error retrieving contacts: {e}")
        return JsonResponse(
            {'error': 'Failed to retrieve contacts.'},
            status=500
        )
