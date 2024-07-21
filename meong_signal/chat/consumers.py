import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from .models import Message, ChatRoom

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # JWT token authentication
        query_string = self.scope['query_string'].decode()
        token_key, token_value = query_string.split('=')

        if token_key != 'token':
            await self.close()
            return
        
        self.user = await self.get_user_from_token(token_value)

        if self.user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await super().disconnect(close_code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.user

        # 메시지를 데이터베이스에 저장
        await self.save_message(self.room_id, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.nickname,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Validate the token
            UntypedToken(token)
            # If token is valid, get the user from the token
            jwt_authenticator = JWTAuthentication()
            validated_token = jwt_authenticator.get_validated_token(token)
            user = jwt_authenticator.get_user(validated_token)
            return user
        except (InvalidToken, TokenError) as e:
            return AnonymousUser()

    @database_sync_to_async
    def save_message(self, room_id, sender, message):
        room = ChatRoom.objects.get(id=room_id)
        Message.objects.create(room=room, sender=sender, content=message)
