from rest_framework.serializers import ModelSerializer
from ..models import Account, FavoriteItem


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'image', 'account_type', 'favorite', "chat"]


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        account = Account(
            username=validated_data['username'],
            email=validated_data['email']
        )
        account.set_password(validated_data["password"])
        account.save()
        return account


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = ["owner", "item", "add_date"]
