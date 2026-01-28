"""
WebSocket URL routing configuration for the entire project.
"""
from django.urls import re_path
from apps.orders.consumers import OrderConsumer, OrderItemConsumer
from apps.tables.consumers import TableConsumer, TableSessionConsumer
from apps.accounts.consumers import WaiterConsumer, RestaurantNotificationConsumer

websocket_urlpatterns = [
    # Order WebSocket endpoints
    re_path(r'ws/orders/(?P<order_id>\w+)/$', OrderConsumer.as_asgi()),
    re_path(r'ws/orders/(?P<order_id>\w+)/items/$', OrderItemConsumer.as_asgi()),
    
    # Table WebSocket endpoints
    re_path(r'ws/tables/(?P<table_id>\w+)/$', TableConsumer.as_asgi()),
    re_path(r'ws/tables/sessions/(?P<session_id>\w+)/$', TableSessionConsumer.as_asgi()),
    
    # Waiter notification endpoints
    re_path(r'ws/waiters/(?P<waiter_id>\w+)/$', WaiterConsumer.as_asgi()),
    re_path(r'ws/restaurants/(?P<restaurant_id>\w+)/notifications/$', WaiterConsumer.as_asgi()),
    
    # Restaurant-wide notifications
    re_path(r'ws/restaurants/(?P<restaurant_id>\w+)/$', RestaurantNotificationConsumer.as_asgi()),
]
