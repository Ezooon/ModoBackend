from django.urls import path
from .views import image, user_image


urlpatterns = [
    path("accounts_images/<str:filename>/", image),
    path("<str:username>/profile/", user_image),
]
