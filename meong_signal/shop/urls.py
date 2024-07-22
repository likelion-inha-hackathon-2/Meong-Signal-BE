from django.contrib import admin
from django.urls import path
from . import views

urlpatterns =[
    path('meong/charge', views.charger_meong),
    path('meong', views.return_meong),
    path('product', views.product),
    path('purchase', views.purchase_product),
    path('category/<str:category>', views.category_product),
]