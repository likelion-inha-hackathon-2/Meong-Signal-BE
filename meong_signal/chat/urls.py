from django.urls import path
from .views import ChatRoomList, ChatRoomDetail, MessageList, ChatRoomMessagesView
from . import views

urlpatterns = [
    path('rooms', ChatRoomList.as_view(), name='chatroom-list'),
    path('rooms/<int:pk>', ChatRoomDetail.as_view(), name='chatroom-detail'),
    path('rooms/<int:room_id>/messages', MessageList.as_view(), name='message-list'),
    path('rooms/<int:room_id>/messages/view', ChatRoomMessagesView.as_view(), name='chatroom-messages-view'),
    path('user1/<int:room_id>', views.user1room, name='chat-room'),
    path('user2/<int:room_id>', views.user2room, name='chat-room'),
]
