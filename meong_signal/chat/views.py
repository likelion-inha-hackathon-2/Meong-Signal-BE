from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatRoom, Message
from .serializer import ChatRoomSerializer, MessageSerializer
from account.models import User

from django.shortcuts import render, get_object_or_404

def room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    return render(request, 'chat/room.html', {
        'room_id': chat_room.id
    })


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


class ChatRoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class MessageList(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Message.objects.filter(room__id=room_id)

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        room = ChatRoom.objects.get(id=room_id)
        serializer.save(room=room, sender=self.request.user)


class ChatRoomMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        messages = Message.objects.filter(room__id=room_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
