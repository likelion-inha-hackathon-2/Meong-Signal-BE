from django.urls import path
from . import views

urlpatterns = [
    path('new', views.new_achievement),
    path('all', views.get_achievement),
    path('user', views.new_achievement_about_user),
    path('achievements/set-represent', views.set_representative)
]