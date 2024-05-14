from django.urls import path
from .views import SignUpView, LoginView, FavoriteView, AccountDetails


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('details/', AccountDetails.as_view()),
    path('sign-up/', SignUpView.as_view()),
    path('favorite/', FavoriteView.as_view()),
    path('favorite/<int:pk>/', FavoriteView.as_view()),
]
