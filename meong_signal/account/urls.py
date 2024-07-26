from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('me', views.get_user_info),
    path('', views.update_user_info),
    path('login/kakao/callback', views.kakao_login_callback),
    path('login/naver/callback', views.naver_login_callback),
    path('login/google/callback', views.google_login_callback),
    path('my-email', views.get_user_email),
]