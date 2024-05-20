from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from .serializers import ItemSerializer, Item, CartSerializer, CreateCartSerializer, Cart, Category, CategorySerializer, CreateItemSerializer
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, status, decorators


class ListItems(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    ordering_fields = ['name', 'price', "?"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = 'name'
    filterset_fields = ['category', 'category__name', 'stock', 'add_by', 'price']
    search_fields = ['name']

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CreateItem(CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = CreateItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        if "category" in request.data:
            category = Category.objects.get_or_create(name=request.data["category"])[0]
            data["category"] = category.id

        data["add_by"] = request.user.id
        data["last_modified"] = timezone.now()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ItemDetail(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = CreateItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = dict(request.data)
        if "category" in request.data:
            category = Category.objects.get_or_create(name=request.data["category"])[0]
            data["category"] = category.id

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ListCarts(ListCreateAPIView):
    queryset = Cart.objects.all()
    ordering_fields = ['add_date']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    ordering = 'add_date'
    filterset_fields = ['add_date', 'user', 'delivered']
    search_fields = ['items', 'user']

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCartSerializer
        return CartSerializer

    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        if request.user.chat.cart:
            return Response({"detail": "finish or cancel your current order first"}, status.HTTP_409_CONFLICT)
        return super().post(request, *args, **kwargs)


class CartDetail(RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.canceled = timezone.now()
        cart.canceled_by = self.request.user
        return Response({'canceled': True}, status.HTTP_200_OK)


class ListCategories(ListAPIView):
    queryset = Category.objects.all()
    search_fields = ['name']
    serializer_class = CategorySerializer
    pagination_class = None


@decorators.api_view(['PATCH'])
@decorators.authentication_classes([TokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
@decorators.parser_classes([FileUploadParser])
def set_item_image(request, pk, filename):
    img = request.data["file"]
    item = Item.objects.get(pk=pk)
    item.image = img
    item.last_modified = timezone.now()
    item.save()
    Response(status=status.HTTP_200_OK)
