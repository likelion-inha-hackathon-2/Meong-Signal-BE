from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('new', views.new_dog),
    path('status/<int:dog_id>', views.update_dog_status),
    path('all', views.dog_list),
    path('boring', views.boring_dog_list),
]