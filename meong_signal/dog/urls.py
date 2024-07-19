from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('new', views.new_dog),
    path('status/<int:dog_id>', views.update_dog_status),
    path('all', views.dog_list),
    path('boring', views.boring_dog_list),
    path('<int:dog_id>/tags', views.get_representative_tags),
    path('search-by-tag/<int:tag_number>', views.search_by_tag),
    path('<int:dog_id>', views.dog_info),
    path('new-only-dog', views.new_dog_only)
]