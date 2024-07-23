from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('newroom', ChatRoomList.as_view(), name='chatroom-list'),
    path('rooms',views.chat_rooms),
    path('user1/<int:room_id>', views.user1room, name='chat-room'),
    path('user2/<int:room_id>', views.user2room, name='chat-room'),
]
