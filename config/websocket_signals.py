"""
Django signals for broadcasting events via WebSockets.
These signals trigger WebSocket group messages when model changes occur.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


@receiver(post_save, sender='orders.Order')
def order_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for Order model changes.
    Broadcasts order updates to WebSocket consumers.
    """
    channel_layer = get_channel_layer()
    
    order_data = {
        'id': instance.id,
        'status': instance.status,
        'status_display': instance.get_status_display(),
        'total_amount': str(instance.total_amount),
        'items_count': instance.items.count(),
        'created_at': instance.created_at.isoformat(),
    }
    
    # Broadcast to order consumers
    async_to_sync(channel_layer.group_send)(
        f'order_{instance.id}',
        {
            'type': 'order_update',
            'data': order_data
        }
    )
    
    # Broadcast to restaurant consumers if order is new
    if created:
        async_to_sync(channel_layer.group_send)(
            f'restaurant_{instance.restaurant.id}',
            {
                'type': 'new_order',
                'data': {
                    'order_id': instance.id,
                    'table_number': instance.table_session.table.number,
                    'items_count': instance.items.count(),
                    'created_at': instance.created_at.isoformat(),
                }
            }
        )
        
        # Notify waiter if assigned
        if instance.waiter:
            async_to_sync(channel_layer.group_send)(
                f'waiter_{instance.waiter.id}',
                {
                    'type': 'order_notification',
                    'data': {
                        'order_id': instance.id,
                        'table_number': instance.table_session.table.number,
                        'items_count': instance.items.count(),
                        'message': f'New order for table {instance.table_session.table.number}'
                    }
                }
            )
    
    # Notify when order is ready
    if instance.status == 'ready':
        async_to_sync(channel_layer.group_send)(
            f'restaurant_{instance.restaurant.id}',
            {
                'type': 'order_ready',
                'data': {
                    'order_id': instance.id,
                    'table_number': instance.table_session.table.number,
                    'message': f'Order ready for table {instance.table_session.table.number}'
                }
            }
        )


@receiver(post_save, sender='tables.Table')
def table_status_changed(sender, instance, **kwargs):
    """
    Signal handler for Table model changes.
    Broadcasts table status updates.
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'table_{instance.id}',
        {
            'type': 'table_status',
            'data': {
                'is_occupied': instance.is_occupied,
                'is_active': instance.is_active,
                'updated_at': timezone.now().isoformat(),
            }
        }
    )
    
    # Broadcast to restaurant consumers
    async_to_sync(channel_layer.group_send)(
        f'restaurant_{instance.restaurant.id}',
        {
            'type': 'table_update',
            'data': {
                'table_id': instance.id,
                'table_number': instance.number,
                'is_occupied': instance.is_occupied,
            }
        }
    )


@receiver(post_save, sender='tables.TableSession')
def table_session_changed(sender, instance, created, **kwargs):
    """
    Signal handler for TableSession model changes.
    """
    channel_layer = get_channel_layer()
    
    if created:
        # Mark table as occupied
        instance.table.is_occupied = True
        instance.table.save(update_fields=['is_occupied'])
        
        # Notify about new session
        async_to_sync(channel_layer.group_send)(
            f'restaurant_{instance.table.restaurant.id}',
            {
                'type': 'restaurant_broadcast',
                'message': f'Guest arrived at table {instance.table.number}'
            }
        )
    
    # Broadcast session status
    async_to_sync(channel_layer.group_send)(
        f'table_session_{instance.id}',
        {
            'type': 'session_update',
            'data': {
                'guests_count': instance.guests_count,
                'updated_at': timezone.now().isoformat(),
            }
        }
    )


@receiver(post_save, sender='payments.Payment')
def payment_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for Payment model changes.
    Broadcasts payment notifications.
    """
    channel_layer = get_channel_layer()
    
    payment_data = {
        'id': instance.id,
        'payment_id': instance.payment_id,
        'status': instance.status,
        'amount': str(instance.amount),
        'created_at': instance.created_at.isoformat(),
    }
    
    if created:
        # Notify about new payment
        if instance.order:
            async_to_sync(channel_layer.group_send)(
                f'waiter_{instance.order.waiter.id}',
                {
                    'type': 'payment_notification',
                    'data': {
                        'payment_id': instance.id,
                        'order_id': instance.order.id,
                        'amount': str(instance.amount),
                        'message': f'Payment of {instance.amount} {instance.currency} received'
                    }
                }
            )
    
    if instance.status == 'completed':
        # Broadcast payment completion
        async_to_sync(channel_layer.group_send)(
            f'restaurant_{instance.table_session.table.restaurant.id if instance.table_session else instance.order.restaurant.id}',
            {
                'type': 'payment_completed',
                'data': payment_data
            }
        )


def ready():
    """
    Django app ready signal handler.
    Import signals when app is ready.
    """
    import apps.orders.models
    import apps.tables.models
    import apps.payments.models
