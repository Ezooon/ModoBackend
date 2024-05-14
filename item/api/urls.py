from django.urls import path
from .views import ItemDetail, ListItems, ListCarts, ListCategories


urlpatterns = [
    path("<int:pk>/", ItemDetail.as_view()),
    path("all-items/", ListItems.as_view()),
    path("carts/", ListCarts.as_view()),
    path("carts/order/", ListCarts.as_view()),
    path("categories/", ListCategories.as_view())
]
