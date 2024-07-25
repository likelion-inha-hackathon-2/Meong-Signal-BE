# http요청이 아닌 websocket요청은 consumers.py에서 처리

from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import *
import json

class LocationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("웹소켓 연결 성공")

        try:          
            self.room_id = self.scope['url_route']['kwargs']['room_id'] # URL 경로에서 방 ID를 추출합니다.

            if not await self.check_room_exists(self.room_id): # 현재 산책중인지 확인합니다.
                raise ValueError('산책 정보가 존재하지 않습니다.')
                        
            group_name = self.get_group_name(self.room_id) # 방 ID를 사용하여 그룹 이름을 얻습니다.

            await self.channel_layer.group_add(group_name, self.channel_name) # 현재 채널을 그룹에 추가합니다.                       
            await self.accept() # WebSocket 연결을 수락합니다.

        except ValueError as e: # 값 오류가 있을 경우 (예: 방이 존재하지 않음), 오류 메시지를 보내고 연결을 종료합니다.           
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        try:            
            group_name = self.get_group_name(self.room_id) # 방 ID를 사용하여 그룹 이름을 얻습니다.
            await self.channel_layer.group_discard(group_name, self.channel_name) # 현재 채널을 그룹에서 제거합니다.

        except Exception as e: # 일반 예외를 처리합니다 (예: 오류 기록).         
            pass

    async def receive_json(self, content):
        try:
            # 수신된 JSON에서 필요한 정보를 추출합니다.
            latitude = content['latitude']
            longitude = content['longitude']
            walk_user_email = content['walk_user_email']
            owner_email = content['owner_email']
            # visitor_user_email = content.get('visitor_user_email')
            print("latitude:", latitude, "longitude:", longitude, "walk_user_email:", walk_user_email, "owner_email:", owner_email)

            # 두 이메일이 모두 제공되었는지 확인합니다.
            if not walk_user_email or not owner_email:
                raise ValueError("견주 및 산책자 이메일이 모두 필요합니다.")

            # 제공된 이메일을 사용하여 방을 가져오거나 생성합니다.
            room = await self.get_or_create_room(walk_user_email, owner_email)
            
            # room_id 속성을 업데이트합니다.
            self.room_id = str(room.id)
            
            # 그룹 이름을 가져옵니다.
            group_name = self.get_group_name(self.room_id)
            
            # 수신된 메시지를 데이터베이스에 저장합니다.
            await self.save_location(room, latitude, longitude, walk_user_email)

            # 메시지를 전체 그룹에 전송합니다.
            await self.channel_layer.group_send(group_name, {
                'type': 'chat_message',
                'latitude': latitude,
                'longitude': longitude
            })

        except ValueError as e:
            # 값 오류가 있을 경우, 오류 메시지를 전송합니다.
            await self.send_json({'error': str(e)})

    async def chat_message(self, event):
        try:
            # 이벤트에서 위, 경도를 추출합니다.
            latitude = event['latitude']
            longitude = event['longitude']
            
            # 추출된 위, 경도를 JSON으로 전달합니다.
            await self.send_json({'latitude': latitude, 'longitude': longitude})
        except Exception as e:
            # 일반 예외를 처리하여 오류 메시지를 보냅니다.
            await self.send_json({'error': '위, 경도 전송 실패'})

    @staticmethod
    def get_group_name(room_id):
        # 방 ID를 사용하여 고유한 그룹 이름을 구성합니다.
        return f"chat_room_{room_id}"
    
    @database_sync_to_async
    def get_or_create_room(self, walk_user_email, owner_email):
        owner, _ = Owner.objects.get_or_create(owner_email = owner_email)
        walk_user, _ = WalkUser.objects.get_or_create(walk_user_email = walk_user_email)

        room, created = WalkRoom.objects.get_or_create(
            owner = owner,
            walk_user = walk_user
        )
        
        return room
    
    @database_sync_to_async
    def save_location(self, room, latitude, longitude, walk_user_email):
        # 위, 경도가 제공되었는지 확인합니다.
        if not latitude or not longitude or not walk_user_email:
            raise ValueError("위, 경도 정보가 필요합니다.")
        
        # 위치 정보를 생성하고 데이터베이스에 저장합니다.
        Location.objects.create(room=room, walk_user_email=walk_user_email, latitude=latitude, longitude=longitude)

    @database_sync_to_async
    def check_room_exists(self, room_id):
        # 주어진 ID로 산책 room이 존재하는지 확인합니다.
        return WalkRoom.objects.filter(id=room_id).exists()