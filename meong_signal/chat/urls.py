from django.urls import path
from .views import ChatRoomList, ChatRoomDetail, MessageList, ChatRoomMessagesView
from . import views

urlpatterns = [
    path('rooms', ChatRoomList.as_view(), name='chatroom-list'),
    path('rooms/<int:pk>', ChatRoomDetail.as_view(), name='chatroom-detail'),
    path('rooms/<int:room_id>/messages', MessageList.as_view(), name='message-list'),
    path('rooms/<int:room_id>/messages/view', ChatRoomMessagesView.as_view(), name='chatroom-messages-view'),
    path('<int:room_id>', views.room, name='chat-room'),
]
