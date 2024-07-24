from django.urls import path, re_path

from walk_status import consumers

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_id>\d+)/locations$', consumers.LocationConsumer.as_asgi()),
]