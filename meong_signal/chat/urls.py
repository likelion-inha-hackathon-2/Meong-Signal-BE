from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('newroom', ChatRoomList.as_view(), name='chatroom-list'),
    path('rooms',views.chat_rooms),
    path('rooms/<int:room_id>', views.enter_chat_room),
    path('rooms/<int:room_id>/data', views.get_chat_messages),
    
    #웹소켓 로컬 작동 테스트용
    path('user1/<int:room_id>', views.user1room, name='chat-room'),
    path('user2/<int:room_id>', views.user2room, name='chat-room'),
]
