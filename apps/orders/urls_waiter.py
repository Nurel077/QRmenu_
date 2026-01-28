"""
Web URLs for orders app (Waiter panel).
"""
from django.urls import path
from django.views.generic import TemplateView

app_name = 'orders_waiter'

urlpatterns = [
    # Waiter panel
    path('dashboard/<slug:restaurant_slug>/', TemplateView.as_view(template_name='waiter_dashboard.html'), name='waiter_dashboard'),
    path('orders/<slug:restaurant_slug>/', TemplateView.as_view(template_name='waiter_orders.html'), name='waiter_orders'),
]
