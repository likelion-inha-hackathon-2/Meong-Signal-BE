from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('written', views.get_written_reviews),
    path('received', views.get_received_reviews),
    path('owner/new', views.new_review_rating)
]