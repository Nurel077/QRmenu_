"""
URL configuration for waiter panel.
"""
from django.urls import path
from .views_waiter import (
    waiter_dashboard,
    waiter_orders,
    waiter_tasks,
    update_order,
    restaurant_statistics
)

app_name = 'waiter'

urlpatterns = [
    # Waiter panel views
    path('', waiter_dashboard, name='dashboard'),
    
    # API endpoints
    path('api/orders/', waiter_orders, name='orders'),
    path('api/tasks/', waiter_tasks, name='tasks'),
    path('api/statistics/', restaurant_statistics, name='statistics'),
    path('api/orders/<str:order_id>/', update_order, name='update-order'),
]
