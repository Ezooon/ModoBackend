from django.urls import path
from .views import (ListMessages, MessageDetail, ListChats, ListUnhandledChats,
                    set_chat_handler, order_delivered, cancel_order, drop_order)


urlpatterns = [
    path("messages/", ListMessages.as_view()),
    path("messages/<int:pk>", MessageDetail.as_view()),
    path("unhandled/", ListUnhandledChats.as_view()),
    path("<int:pk>/handle/", set_chat_handler),
    path("<int:pk>/delivered/", order_delivered),
    path("<int:pk>/cancel/", cancel_order),
    path("<int:pk>/drop/", drop_order),
    path("all/", ListChats.as_view())
]
