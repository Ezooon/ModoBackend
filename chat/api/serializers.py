from rest_framework.serializers import ModelSerializer, ImageField
from ..models import Message, Chat
from item.api.serializers import CartSerializer


class ChatSerializer(ModelSerializer):
    cart = CartSerializer()
    image = ImageField()

    class Meta:
        model = Chat
        fields = ["id", "chat_name", "image", "owner", "handler", "cart"]


class MessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "id",
            "chat",
            "sent_by",
            "sent_to",
            "content",
            "delivered",
            "read",
            "sent",
        ]
