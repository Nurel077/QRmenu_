"""
Admin configuration for payments app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Payment model."""
    
    list_display = ['payment_link', 'order_link', 'amount_display', 'payment_type_badge', 'status_badge', 
                    'payer_display', 'created_at']
    list_filter = ['status', 'payment_type', 'created_at', 'order__table_session__table__restaurant']
    search_fields = ['payment_id', 'order__id', 'payer_name', 'payer_phone', 'payer_email']
    ordering = ['-created_at']
    readonly_fields = ('payment_id', 'created_at', 'updated_at')
    actions = ['mark_completed', 'mark_failed']
    
    fieldsets = (
        (_('Идентификация'), {
            'fields': ('payment_id', 'order', 'table_session')
        }),
        (_('Информация о платеже'), {
            'fields': ('payment_type', 'status', 'amount', 'currency')
        }),
        (_('Плательщик'), {
            'fields': ('payer_name', 'payer_phone', 'payer_email')
        }),
        (_('Описание'), {
            'fields': ('description', 'notes')
        }),
        (_('Данные транзакции'), {
            'fields': ('transaction_id', 'external_reference'),
            'classes': ('collapse',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_link(self, obj):
        """Display payment ID with link."""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:payments_payment_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_id[:8])
    payment_link.short_description = _('Payment ID')
    
    def order_link(self, obj):
        """Display order link."""
        from django.utils.html import format_html
        if obj.order:
            from django.urls import reverse
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">#{}</a>', url, obj.order.id)
        return '—'
    order_link.short_description = _('Order')
    
    def amount_display(self, obj):
        """Display amount with currency."""
        from django.utils.html import format_html
        return format_html(
            '<span style="font-weight: bold; color: green;">{} {}</span>',
            obj.amount, obj.currency
        )
    amount_display.short_description = _('Amount')
    
    def payment_type_badge(self, obj):
        """Display payment type badge."""
        from django.utils.html import format_html
        icons = {'cash': '💵', 'card': '💳', 'qr': 'QR', 'mobile': '📱'}
        icon = icons.get(obj.payment_type, '💰')
        return format_html('{} {}', icon, obj.get_payment_type_display())
    payment_type_badge.short_description = _('Type')
    
    def status_badge(self, obj):
        """Display payment status badge."""
        from django.utils.html import format_html
        colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def payer_display(self, obj):
        """Display payer info."""
        return obj.payer_name or obj.payer_email or '—'
    payer_display.short_description = _('Payer')
    
    def mark_completed(self, request, queryset):
        """Mark payments as completed."""
        updated = queryset.filter(status='pending').update(status='completed')
        self.message_user(request, f'{updated} payments marked as completed.')
    mark_completed.short_description = _('✓ Mark as completed')
    
    def mark_failed(self, request, queryset):
        """Mark payments as failed."""
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_failed.short_description = _('✗ Mark as failed')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(
                order__table_session__table__restaurant=request.user.restaurant
            ) | qs.filter(
                table_session__table__restaurant=request.user.restaurant
            )
        if request.user.is_waiter:
            return qs.filter(
                order__table_session__table__restaurant=request.user.restaurant
            ) | qs.filter(
                table_session__table__restaurant=request.user.restaurant
            )
        return qs.none()
