from django.contrib import admin
from django.urls import path
from . import views

urlpatterns =[
    path('meong', views.charger_meong),
    path('product', views.product),
    path('purchase', views.purchase_product),
    path('category/<str:category>', views.category_product),
]