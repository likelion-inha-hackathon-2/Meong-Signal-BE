from django.urls import path
from . import views

urlpatterns = [
    path('new', views.new_achievement),
    path('all', views.get_achievement)
]