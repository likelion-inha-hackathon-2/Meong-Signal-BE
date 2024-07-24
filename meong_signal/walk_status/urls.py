from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.WalkRoomListCreateView.as_view(), name='walk_rooms'),
    path('<int:room_id>/locations', views.LocationListView.as_view(), name='walk_status_locations'),
]