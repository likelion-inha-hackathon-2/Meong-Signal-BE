from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('appointment', views.create_schedule),
    path('upcoming', views.get_upcoming_schedules),
]