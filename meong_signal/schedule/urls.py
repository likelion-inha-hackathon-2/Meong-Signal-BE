from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('appointment', views.create_schedule),
    path('upcoming', views.get_upcoming_schedules),
    path('<int:schedule_id>', views.update_schedule),
    path('walking-dogs', views.get_walking_dogs),
    path('del/<int:app_id>', views.delete_appointment),
]