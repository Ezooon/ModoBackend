from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, status

from .serializers import Message, MessageSerializer


class ListMessages(mixins.UpdateModelMixin, ListCreateAPIView):
    serializer_class = MessageSerializer
    ordering_fields = ['sent']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    pagination_class = None
    ordering = 'sent'
    filterset_fields = ['sent_to', 'sent_by', 'sent', 'delivered', 'read']
    search_fields = ['chat', 'sent_to', 'sent_by', 'content']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.chat.messages.all()  # ToDo for other chats check the request.body and add an if block

    def get(self, request, *args, **kwargs):
        wait_list = request.data.get("wait_list")
        if not wait_list:
            return super().get(request, *args, **kwargs)
        msgs = self.get_queryset().in_bulk(wait_list)
        serializer = MessageSerializer([msgs[i] for i in msgs], many=True)
        return Response(serializer.data)

    def put(self, request, *_, **__):
        """mark all messages as delivered or delivered and read"""
        queryset = self.filter_queryset(self.get_queryset())
        delivered = request.query_params.get("delivered")
        read = request.query_params.get("read")

        if delivered:
            for msg in queryset:
                msg.delivered = True
            Message.objects.bulk_update(queryset, ["delivered"])

        if read:
            for msg in queryset:
                msg.read = True
            Message.objects.bulk_update(queryset, ["read"])

        return Response({"updated": delivered or read}, 200)

    def post(self, request, *args, **kwargs):
        if "chat" not in request.data:
            request.data["chat"] = request.user.chat.id
        if "sent_to" not in request.data:
            if request.data["chat"] == request.user.chat.id:
                if request.user.chat.handler:
                    request.data["sent_to"] = request.user.chat.handler.id
            else:
                request.data["sent_to"] = request.data["chat"].owner.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    pagination_class = None
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
