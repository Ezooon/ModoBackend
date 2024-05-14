from .serializers import SignUpSerializer, Account, FavoriteSerializer, FavoriteItem, AccountSerializer
from item.api.serializers import ItemSerializer
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status


class SignUpView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = SignUpSerializer


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'token': token.key,
        })


class FavoriteView(ListCreateAPIView):
    serializer_class = FavoriteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None
    ordering = "add_date"

    def get_queryset(self):
        return FavoriteItem.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        if "simple" in self.request.query_params.get("results"):
            return super().get(request, *args, **kwargs)
        items = request.user.favorite.all()
        return Response(ItemSerializer(items, many=True, context=self.get_serializer_context()).data)

    def post(self, request, pk):
        fav_items = request.user.list_favorite_item_ids()

        if pk not in fav_items:
            data = {"owner": request.user.pk, "item": pk}
            new = FavoriteItem()
            new_serializer = self.get_serializer(new, data=data)
            new_serializer.is_valid()
            new_serializer.save()
        else:
            self.get_queryset().get(item__pk=pk).delete()

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetails(RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        pass  # ToDo you just can't leave it like this
