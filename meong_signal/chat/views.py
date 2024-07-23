from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ChatRoom, Message
from .serializer import *
from account.models import User

from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema

def user1room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    return render(request, 'chat/user1.html', {
        'room_id': chat_room.id
    })


def user2room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    return render(request, 'chat/user2.html', {
        'room_id': chat_room.id
    })


############################
# 두 유저(견주 - 사용자) 간 채팅방을 만드는 api

class ChatRoomList(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        owner_user_id = request.data.get('owner_user')
        user_user_id = request.data.get('user_user')

        if not (User.objects.filter(id=owner_user_id).exists() and User.objects.filter(id=user_user_id).exists()):
            return Response({'error': 'One or both users do not exist.'}, status=400)

        return super().create(request, *args, **kwargs)
    
############################

############################
# 채팅방 목록을 반환하는 api


@swagger_auto_schema(
    method="GET",
    tags=["chat api"],
    operation_summary="채팅방 목록 조회",
    responses={
        200: ChatRoomInfoSerializer(many=True),
        401: 'Unauthorized'
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def chat_rooms(request):
    user = request.user
    rooms = ChatRoom.objects.filter(owner_user=user) | ChatRoom.objects.filter(user_user=user)

    chat_rooms_data = []
    for room in rooms:
        if room.owner_user == user:
            other_user = room.user_user
        else:
            other_user = room.owner_user

        last_message = Message.objects.filter(room=room).order_by('-id').first()
        last_message_data = {
            'last_message_content': last_message.content if last_message else None,
            'last_message_timestamp': last_message.timestamp if last_message else None
        }

        room_data = {
            'room_id': room.id,
            'other_user_nickname': other_user.nickname,
            'other_user_profile_image': other_user.profile_image.url if other_user.profile_image else None,
            'last_message_content': last_message_data['last_message_content'],
            'last_message_timestamp': last_message_data['last_message_timestamp'],
        }
        chat_rooms_data.append(room_data)

    serializer = ChatRoomInfoSerializer(chat_rooms_data, many=True)
    return Response(serializer.data)

############################