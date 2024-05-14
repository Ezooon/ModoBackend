from rest_framework.serializers import ModelSerializer, ImageField
from ..models import Message


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
