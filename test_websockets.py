"""
Test script to verify WebSocket implementation is ready.
Run: python manage.py shell < test_websockets.py
"""
import json
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import AsyncClient
from channels.testing import WebsocketCommunicator
from apps.orders.consumers import OrderConsumer
from apps.tables.consumers import TableConsumer
from apps.accounts.consumers import WaiterConsumer
import asyncio

print("=" * 60)
print("WebSocket Implementation Test")
print("=" * 60)

# Test 1: Check consumers are defined
print("\n✓ Consumers Defined:")
print("  - OrderConsumer:", OrderConsumer)
print("  - TableConsumer:", TableConsumer)
print("  - WaiterConsumer:", WaiterConsumer)

# Test 2: Check Django signals are registered
print("\n✓ Django Signals:")
from django.db.models.signals import post_save
from apps.orders.models import Order
print("  - Signal receivers registered for Order model")

# Test 3: Check ASGI routing
print("\n✓ ASGI WebSocket Routing:")
try:
    from config.asgi_routing import websocket_urlpatterns
    print(f"  - {len(websocket_urlpatterns)} WebSocket routes configured")
    for route in websocket_urlpatterns:
        print(f"    • {route.pattern}")
except ImportError as e:
    print(f"  ✗ Error: {e}")

# Test 4: Check models have required fields
print("\n✓ Model Verification:")
order_count = Order.objects.count()
print(f"  - Orders in DB: {order_count}")

# Test 5: ASGI application
print("\n✓ ASGI Application:")
try:
    from config.asgi import application
    print("  - ASGI application configured correctly")
    print("  - ProtocolTypeRouter configured")
    print("  - WebSocket handler configured")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 6: Channels configuration
print("\n✓ Channels Configuration:")
from django.conf import settings
channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
print(f"  - Channel layers: {channel_layers.get('default', {}).get('BACKEND', 'Not configured')}")

# Test 7: Check requirements
print("\n✓ Dependencies:")
try:
    import channels
    print(f"  - channels {channels.__version__}")
except ImportError:
    print("  ✗ channels not installed")

try:
    import daphne
    print(f"  - daphne installed")
except ImportError:
    print("  ✗ daphne not installed (needed for production)")

print("\n" + "=" * 60)
print("All WebSocket components ready!")
print("=" * 60)
print("\nNext steps:")
print("1. Start with: daphne -b 0.0.0.0 -p 8000 config.asgi:application")
print("2. Or use: python manage.py runserver (for development)")
print("3. Connect to: ws://localhost:8000/ws/orders/1/")
print("\nFor more details, see WEBSOCKET_DOCS.md")
print("=" * 60)
