from rest_framework import serializers
from myapp.models import Contact
from myapp.repositories.users_contacts_repository import UsersContactsRepository

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'title', 'public_account_id', 'account_name', 'currency_code']

    def validate_public_account_id(self, value):
        repo = UsersContactsRepository()
        if not repo.account_exists(value):
            raise serializers.ValidationError("Public account ID does not exist.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return self.context['service'].create_contact(
            user,
            validated_data['title'],
            validated_data['public_account_id'],
            validated_data['account_name'],
            validated_data['currency_code']
        )