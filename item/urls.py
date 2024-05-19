from django.urls import path
from .views import image


urlpatterns = [
    path("item_images/<str:filename>", image),
]
