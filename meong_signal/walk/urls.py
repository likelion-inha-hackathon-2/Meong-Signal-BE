from django.urls import path
from . import views

urlpatterns = [
    path('coordinate', views.coordinate, name='coordinate'),
    path('trails', views.save_nearby_trails,name='save_nearby_trails'),
    path('new', views.new_walk),
    path('all', views.walk_all)
]