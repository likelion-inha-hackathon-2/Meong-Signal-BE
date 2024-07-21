import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # JWT token authentication
        query_string = self.scope['query_string'].decode()
        print(f"Query string: {query_string}")  # Query string 값을 출력하여 확인

        token_key, token_value = query_string.split('=', 1)
        print(f"Token key: {token_key}, Token value: {token_value}")  # Token key와 value 값을 출력하여 확인

        if token_key != 'token':
            print("Invalid token key")
            await self.close()
            return
        
        self.user = await self.get_user_from_token(token_value)

        if self.user.is_anonymous:
            print("Anonymous user")
            await self.close()
        else:
            try:
                print('self.channel_layer:', self.channel_layer)
                print('self.channel_name:', self.channel_name)
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                print('Added to group')
                await self.accept()
            except Exception as e:
                print(f"Error during group add or accept: {e}")
                await self.close()

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
            print(f"Token error: {str(e)}")
            return AnonymousUser()
