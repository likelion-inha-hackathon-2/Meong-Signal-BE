from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('me', views.get_user_info),
    path('', views.update_user_info),
]