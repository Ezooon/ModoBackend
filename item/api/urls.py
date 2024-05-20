from django.urls import path
from .views import ItemDetail, ListItems, ListCarts, ListCategories, CartDetail, CreateItem, set_item_image


urlpatterns = [
    path("<int:pk>/", ItemDetail.as_view()),
    path("<int:pk>/image/<str:filename>/", set_item_image),
    path("all-items/", ListItems.as_view()),
    path("", CreateItem.as_view()),
    path("carts/", ListCarts.as_view()),
    path("carts/order/", ListCarts.as_view()),
    path("categories/", ListCategories.as_view()),
    path("carts/<int:pk>/", CartDetail.as_view())
]
