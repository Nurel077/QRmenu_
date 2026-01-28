"""
WebSocket Consumers for waiter notifications.
Real-time waiter alerts and task updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class WaiterConsumer(AsyncWebsocketConsumer):
    """
    Consumer for waiter notifications.
    Handles real-time alerts and task updates for waiters.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.waiter_id = self.scope['url_route']['kwargs'].get('waiter_id')
        self.restaurant_id = self.scope['url_route']['kwargs'].get('restaurant_id')
        
        # Use restaurant group if waiter_id not provided
        if not self.waiter_id and self.restaurant_id:
            self.group_name = f'restaurant_{self.restaurant_id}_waiters'
        else:
            self.group_name = f'waiter_{self.waiter_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to waiter notifications',
            'group': self.group_name
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'acknowledge':
                notification_id = data.get('notification_id')
                await self.acknowledge_notification(notification_id)
            elif action == 'get_tasks':
                tasks = await self.get_waiter_tasks()
                await self.send(text_data=json.dumps({
                    'type': 'tasks_list',
                    'tasks': tasks
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    # Receive message from waiter group
    async def order_notification(self, event):
        """Send order notification to waiter."""
        await self.send(text_data=json.dumps({
            'type': 'order_notification',
            'data': event['data']
        }))
    
    async def payment_notification(self, event):
        """Send payment notification to waiter."""
        await self.send(text_data=json.dumps({
            'type': 'payment_notification',
            'data': event['data']
        }))
    
    async def task_notification(self, event):
        """Send task notification to waiter."""
        await self.send(text_data=json.dumps({
            'type': 'task_notification',
            'data': event['data']
        }))
    
    async def alert(self, event):
        """Send alert to waiter."""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'message': event['message'],
            'priority': event.get('priority', 'normal')
        }))
    
    @database_sync_to_async
    def get_waiter_tasks(self):
        """Get pending tasks for waiter."""
        try:
            from apps.orders.models import Order
            
            # Get pending orders for waiter
            pending_orders = Order.objects.filter(
                waiter_id=self.waiter_id,
                status__in=['pending', 'confirmed', 'ready']
            ).values(
                'id', 'table_session__table__number',
                'status', 'created_at', 'items_count'
            )[:10]
            
            return list(pending_orders)
        except Exception:
            return []
    
    @database_sync_to_async
    def acknowledge_notification(self, notification_id):
        """Acknowledge notification received."""
        # This would save acknowledgment in a Notification model if needed
        pass


class RestaurantNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for restaurant-wide notifications.
    Sends notifications to all staff in a restaurant.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.group_name = f'restaurant_{self.restaurant_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_status':
                status = await self.get_restaurant_status()
                await self.send(text_data=json.dumps({
                    'type': 'restaurant_status',
                    'data': status
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    # Receive messages from restaurant group
    async def new_order(self, event):
        """Notify about new order."""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'data': event['data']
        }))
    
    async def order_ready(self, event):
        """Notify when order is ready."""
        await self.send(text_data=json.dumps({
            'type': 'order_ready',
            'data': event['data']
        }))
    
    async def payment_completed(self, event):
        """Notify about payment completion."""
        await self.send(text_data=json.dumps({
            'type': 'payment_completed',
            'data': event['data']
        }))
    
    async def restaurant_broadcast(self, event):
        """Send broadcast message to restaurant."""
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def get_restaurant_status(self):
        """Get current restaurant status."""
        try:
            from apps.restaurants.models import Restaurant
            from apps.orders.models import Order
            from apps.tables.models import Table
            
            restaurant = Restaurant.objects.get(id=self.restaurant_id)
            active_orders = Order.objects.filter(
                restaurant=restaurant,
                status__in=['pending', 'confirmed', 'ready']
            ).count()
            
            occupied_tables = Table.objects.filter(
                restaurant=restaurant,
                is_occupied=True
            ).count()
            
            return {
                'restaurant_id': self.restaurant_id,
                'name': restaurant.name,
                'active_orders': active_orders,
                'occupied_tables': occupied_tables,
            }
        except Exception:
            return {}
