from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ItemSerializer, Item, CartSerializer, CreateCartSerializer, Cart, Category, CategorySerializer
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters, status


class ListItems(ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    ordering_fields = ['name', 'price', "?"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = 'name'
    filterset_fields = ['category', 'category__name', 'stock', 'add_by', 'price']
    search_fields = ['name']#, 'description']

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ItemDetail(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


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
