from django.urls import path
from . import views

urlpatterns = [
    path('coordinate', views.coordinate, name='coordinate'),
    path('trails', views.save_nearby_trails,name='save_nearby_trails'),
    path('new', views.new_walk),
    path('all', views.walk_all),
    path('toggle/<int:trail_id>', views.toggle_trail),
    path('mark', views.saved_trails),
    path('nonmark', views.recommended_trails),
]