from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, mixins, ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import filters, status, decorators

from .serializers import Message, MessageSerializer, Chat, ChatSerializer


class ListChats(ListAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()
    ordering_fields = ['cart__add_date']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = 'cart__add_date'
    filterset_fields = ['owner', 'cart', 'handler']
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ListUnhandledChats(ListAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.exclude(cart=None).filter(handler=None)
    ordering_fields = ['cart__add_date']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = 'cart__add_date'
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class ListMessages(mixins.UpdateModelMixin, ListCreateAPIView):
    serializer_class = MessageSerializer
    ordering_fields = ['sent']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    pagination_class = None
    ordering = 'sent'
    filterset_fields = ['chat', 'sent_to', 'sent_by', 'sent', 'delivered', 'read']
    search_fields = ['chat', 'sent_to', 'sent_by', 'content']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get("chat") or self.request.data.get("wait_list"):
            return Message.objects.all()
        return self.request.user.chat.messages.all()

    def get(self, request, *args, **kwargs):
        wait_list = request.data.get("wait_list")
        if wait_list:
            msgs = self.get_queryset().in_bulk(id_list=wait_list)
            serializer = MessageSerializer([msgs[i] for i in msgs], many=True)
            return Response(serializer.data)

        after = request.data.get("after")
        if after:
            queryset = self.filter_queryset(self.get_queryset().filter(sent__gte=after))
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().get(request, *args, **kwargs)

    def put(self, request, *_, **__):
        """mark all messages as delivered or delivered and read"""
        queryset = self.filter_queryset(self.get_queryset())
        delivered = request.query_params.get("delivered")
        read = request.query_params.get("read")

        if delivered is not None:
            for msg in queryset:
                msg.delivered = True
            Message.objects.bulk_update(queryset, ["delivered"])
            delivered = True

        if read is not None:
            for msg in queryset:
                msg.read = True
            Message.objects.bulk_update(queryset, ["read"])
            read = True

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


@decorators.api_view(['PUT'])
@decorators.authentication_classes([TokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
def set_chat_handler(request, pk):
    chat = Chat.objects.get(pk=pk)
    if chat.handler:
        return Response({"failed": str(chat.handler) + "is already handling this order"}, status.HTTP_409_CONFLICT)
    Message.objects.create(
        chat=chat,
        sent_by=request.user,
        sent_to=chat.owner,
        content=request.user.greating_message,
    )
    chat.handler = request.user
    chat.save()
    return Response({"handler": str(request.user.id)}, status.HTTP_200_OK)


@decorators.api_view(['PUT'])
@decorators.authentication_classes([TokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
def cancel_order(request, pk):
    chat = Chat.objects.get(pk=pk)
    chat.handler = None
    chat.cart.canceled_by = request.user
    chat.cart.canceled = timezone.now()
    Message.objects.create(
        chat=chat,
        sent_by=request.user,
        sent_to=chat.owner,
        content="your or order was canceled by " + request.user.username,
    )
    chat.cart.save()
    chat.cart = None
    chat.save()
    return Response({"detail": "order was canceled successfully"}, status.HTTP_200_OK)


@decorators.api_view(['PUT'])
@decorators.authentication_classes([TokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
def order_delivered(request, pk):
    chat = Chat.objects.get(pk=pk)
    chat.handler = None
    chat.cart.delivered_by = request.user
    chat.cart.delivered = timezone.now()
    Message.objects.create(
        chat=chat,
        sent_by=request.user,
        sent_to=chat.owner,
        content="Thank you for using our service!",
    )
    chat.cart.save()
    chat.cart = None
    chat.save()
    return Response({"detail": "order is marked as delivered"}, status.HTTP_200_OK)


@decorators.api_view(['PUT'])
@decorators.authentication_classes([TokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
def drop_order(request, pk):
    chat = Chat.objects.get(pk=pk)
    chat.handler = None
    Message.objects.create(
        chat=chat,
        sent_by=request.user,
        sent_to=chat.owner,
        content=request.user.username + \
               " stopped handling your order, please wait for another employee to be asigned to you.",
    )
    chat.save()
    return Response({"detail": "order was canceled successfully"}, status.HTTP_200_OK)
