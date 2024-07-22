from django.urls import path
from . import views

urlpatterns = [
    path('coordinate', views.coordinate, name='coordinate'),
    path('recommended-trails', views.get_nearby_trails,name='save_nearby_trails'),
    path('new', views.new_walk),
    path('all', views.walk_all),
    path('toggle', views.toggle_trail),
    path('<int:trail_id>', views.delete_trail),
    path('mark', views.saved_trails),
    path('user-image/<int:walk_id>', views.walk_user_image),
    path('walks/walk-review-info', views.walk_and_review_info),
]