from django.urls import path
from .views import ListMessages, MessageDetail


urlpatterns = [
    path("messages/", ListMessages.as_view()),
    path("messages/<int:pk>", MessageDetail.as_view()),
]
