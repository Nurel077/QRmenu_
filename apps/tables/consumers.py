"""
WebSocket Consumers for tables app.
Real-time table status updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Table, TableSession


class TableConsumer(AsyncWebsocketConsumer):
    """
    Consumer for table status updates.
    Handles real-time table changes and availability.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.table_id = self.scope['url_route']['kwargs']['table_id']
        self.table_group_name = f'table_{self.table_id}'
        
        await self.channel_layer.group_add(
            self.table_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial table status
        table_data = await self.get_table_data()
        if table_data:
            await self.send(text_data=json.dumps({
                'type': 'table_status',
                'data': table_data
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.table_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'occupy':
                await self.set_table_occupied(True)
            elif action == 'release':
                await self.set_table_occupied(False)
            elif action == 'get_status':
                table_data = await self.get_table_data()
                await self.send(text_data=json.dumps({
                    'type': 'table_status',
                    'data': table_data
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    # Receive message from table group
    async def table_update(self, event):
        """Send table update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'table_update',
            'data': event['data']
        }))
    
    async def table_status(self, event):
        """Send table status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'table_status',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_table_data(self):
        """Get table data from database."""
        try:
            table = Table.objects.select_related('restaurant').get(id=self.table_id)
            current_session = table.current_session
            
            return {
                'id': table.id,
                'number': table.number,
                'capacity': table.capacity,
                'is_occupied': table.is_occupied,
                'is_active': table.is_active,
                'zone': table.zone,
                'restaurant': table.restaurant.name,
                'session': {
                    'id': current_session.id,
                    'session_code': current_session.session_code,
                    'guests_count': current_session.guests_count,
                    'started_at': current_session.started_at.isoformat(),
                } if current_session else None
            }
        except Table.DoesNotExist:
            return None
    
    @database_sync_to_async
    def set_table_occupied(self, occupied):
        """Update table occupied status."""
        try:
            table = Table.objects.get(id=self.table_id)
            table.is_occupied = occupied
            table.save(update_fields=['is_occupied'])
            
            # Broadcast status change
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                self.table_group_name,
                {
                    'type': 'table_status',
                    'data': {
                        'is_occupied': occupied,
                        'updated_at': 'now'
                    }
                }
            )
        except Table.DoesNotExist:
            pass


class TableSessionConsumer(AsyncWebsocketConsumer):
    """
    Consumer for table session updates.
    Handles guest count and session status.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'table_session_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial session status
        session_data = await self.get_session_data()
        if session_data:
            await self.send(text_data=json.dumps({
                'type': 'session_status',
                'data': session_data
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'update_guests_count':
                guests_count = data.get('guests_count')
                await self.update_guests_count(guests_count)
            elif action == 'close_session':
                await self.close_session()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def session_update(self, event):
        """Send session update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'session_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_session_data(self):
        """Get session data from database."""
        try:
            session = TableSession.objects.select_related('table', 'table__restaurant').get(id=self.session_id)
            
            return {
                'id': session.id,
                'session_code': session.session_code,
                'table_number': session.table.number,
                'restaurant': session.table.restaurant.name,
                'guests_count': session.guests_count,
                'started_at': session.started_at.isoformat(),
                'closed_at': session.closed_at.isoformat() if session.closed_at else None,
            }
        except TableSession.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_guests_count(self, guests_count):
        """Update guest count for session."""
        try:
            session = TableSession.objects.get(id=self.session_id)
            session.guests_count = guests_count
            session.save(update_fields=['guests_count'])
            
            # Broadcast update
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                self.session_group_name,
                {
                    'type': 'session_update',
                    'data': {'guests_count': guests_count}
                }
            )
        except TableSession.DoesNotExist:
            pass
    
    @database_sync_to_async
    def close_session(self):
        """Close the session."""
        from django.utils import timezone
        try:
            session = TableSession.objects.get(id=self.session_id)
            session.closed_at = timezone.now()
            session.save(update_fields=['closed_at'])
            
            # Update table
            session.table.is_occupied = False
            session.table.save(update_fields=['is_occupied'])
        except TableSession.DoesNotExist:
            pass
