"""
WebSocket Consumers for orders app.
Real-time order status updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order, OrderItem


class OrderConsumer(AsyncWebsocketConsumer):
    """
    Consumer for order status updates.
    Handles real-time order changes and notifications.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_group_name = f'order_{self.order_id}'
        
        # Join order group
        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial order status
        order_data = await self.get_order_data()
        if order_data:
            await self.send(text_data=json.dumps({
                'type': 'order_status',
                'data': order_data
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'update_status':
                new_status = data.get('status')
                await self.update_order_status(new_status)
            elif action == 'get_status':
                order_data = await self.get_order_data()
                await self.send(text_data=json.dumps({
                    'type': 'order_status',
                    'data': order_data
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    # Receive message from order group
    async def order_update(self, event):
        """Send order update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data']
        }))
    
    async def order_status(self, event):
        """Send order status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'order_status',
            'data': event['data']
        }))
    
    async def order_items_update(self, event):
        """Send order items update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'order_items_update',
            'items': event['items']
        }))
    
    @database_sync_to_async
    def get_order_data(self):
        """Get order data from database."""
        try:
            order = Order.objects.get(id=self.order_id)
            items = OrderItem.objects.filter(order=order).values(
                'id', 'menu_item__name', 'quantity', 'price'
            )
            return {
                'id': order.id,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total_amount': str(order.total_amount),
                'items_count': order.items.count(),
                'items': list(items),
                'created_at': order.created_at.isoformat(),
                'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
                'ready_at': order.ready_at.isoformat() if order.ready_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            }
        except Order.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_order_status(self, new_status):
        """Update order status in database."""
        try:
            order = Order.objects.get(id=self.order_id)
            if new_status in [status[0] for status in Order.STATUS_CHOICES]:
                order.status = new_status
                order.save(update_fields=['status'])
                
                # Broadcast status change to all consumers in group
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    self.order_group_name,
                    {
                        'type': 'order_status',
                        'data': {
                            'status': new_status,
                            'status_display': order.get_status_display()
                        }
                    }
                )
        except Order.DoesNotExist:
            pass


class OrderItemConsumer(AsyncWebsocketConsumer):
    """
    Consumer for order item updates.
    Handles real-time updates for items in an order.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.items_group_name = f'order_items_{self.order_id}'
        
        await self.channel_layer.group_add(
            self.items_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.items_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_items':
                items_data = await self.get_order_items()
                await self.send(text_data=json.dumps({
                    'type': 'items_list',
                    'items': items_data
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def items_updated(self, event):
        """Send items update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'items_updated',
            'items': event['items']
        }))
    
    @database_sync_to_async
    def get_order_items(self):
        """Get order items from database."""
        try:
            items = OrderItem.objects.filter(order_id=self.order_id).values(
                'id', 'menu_item__name', 'quantity', 'price', 'menu_item__image'
            )
            return list(items)
        except Exception:
            return []
