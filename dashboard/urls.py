from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.manage_products, name='manage_products'),
    path('orders/', views.manage_orders, name='manage_orders'),
    path('orders/update-status/', views.update_order_status, name='update_order_status'),
    path('users/', views.manage_users, name='manage_users'),
]
