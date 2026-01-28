"""
Admin configuration for orders app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Enhanced inline admin for OrderItems."""
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity', 'price_display', 'subtotal_display')
    readonly_fields = ('price_display', 'subtotal_display')
    
    def price_display(self, obj):
        """Display price with currency."""
        from django.utils.html import format_html
        return format_html('${:.2f}', obj.price)
    price_display.short_description = _('Price')
    
    def subtotal_display(self, obj):
        """Display subtotal."""
        from django.utils.html import format_html
        total = float(obj.quantity) * float(obj.price)
        return format_html('<strong>${:.2f}</strong>', total)
    subtotal_display.short_description = _('Subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Order model."""
    
    list_display = ['order_link', 'table_display', 'status_badge', 'payment_badge', 'total_display', 
                    'waiter', 'timeline_display']
    list_filter = ['status', 'payment_method', 'created_at', 'table_session__table__restaurant']
    search_fields = ['id', 'guest_name', 'table_session__table__number', 'waiter__username']
    ordering = ['-created_at']
    readonly_fields = ('subtotal', 'tax_amount', 'service_charge_amount', 
                      'total_amount', 'items_count', 'created_at', 'confirmed_at',
                      'ready_at', 'delivered_at', 'paid_at', 'cancelled_at', 'updated_at', 'order_timeline')
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_ready', 'mark_delivered', 'mark_paid']
    
    fieldsets = (
        (_('Заказ'), {
            'fields': ('table_session', 'guest_session', 'guest_name', 'table')
        }),
        (_('Официант'), {
            'fields': ('waiter',)
        }),
        (_('Статус'), {
            'fields': ('status', 'payment_method')
        }),
        (_('Заметки'), {
            'fields': ('notes', 'waiter_notes')
        }),
        (_('Сумма'), {
            'fields': ('subtotal', 'tax_amount', 'service_charge_amount', 'total_amount'),
            'classes': ('collapse',)
        }),
        (_('Статистика'), {
            'fields': ('items_count',),
            'classes': ('collapse',)
        }),
        (_('Время'), {
            'fields': ('order_timeline',)
        }),
    )
    
    def order_link(self, obj):
        """Display order ID with link."""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="#">#{}</a>', obj.id)
    order_link.short_description = _('Order')
    
    def table_display(self, obj):
        """Display table number."""
        return f'Table {obj.table_session.table.number}'
    table_display.short_description = _('Table')
    
    def status_badge(self, obj):
        """Display order status with badge."""
        from django.utils.html import format_html
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'ready': '#28a745',
            'delivered': '#007bff',
            'paid': '#6f42c1',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    
    def payment_badge(self, obj):
        """Display payment method badge."""
        from django.utils.html import format_html
        icons = {'cash': '💵', 'card': '💳', 'qr': 'QR'}
        icon = icons.get(obj.payment_method, '💰')
        return format_html('{} {}', icon, obj.get_payment_method_display())
    payment_badge.short_description = _('Payment')
    
    def total_display(self, obj):
        """Display total amount formatted."""
        from django.utils.html import format_html
        return format_html(
            '<span style="font-weight: bold; color: green;">${:.2f}</span>',
            obj.total_amount
        )
    total_display.short_description = _('Total')
    
    def timeline_display(self, obj):
        """Display order timeline."""
        from django.utils.html import format_html
        times = []
        if obj.created_at:
            times.append(f"📝 {obj.created_at.strftime('%H:%M')}")
        if obj.confirmed_at:
            times.append(f"✓ {obj.confirmed_at.strftime('%H:%M')}")
        if obj.ready_at:
            times.append(f"🍽️ {obj.ready_at.strftime('%H:%M')}")
        return format_html(' → '.join(times) if times else '—')
    timeline_display.short_description = _('Timeline')
    
    def order_timeline(self, obj):
        """Display detailed order timeline."""
        from django.utils.html import format_html
        return format_html(
            '<div style="line-height: 1.8;">'
            '<strong>📝 Created:</strong> {}<br>'
            '<strong>✓ Confirmed:</strong> {}<br>'
            '<strong>🍽️ Ready:</strong> {}<br>'
            '<strong>📦 Delivered:</strong> {}<br>'
            '<strong>💳 Paid:</strong> {}<br>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else '—',
            obj.confirmed_at.strftime('%Y-%m-%d %H:%M') if obj.confirmed_at else '—',
            obj.ready_at.strftime('%Y-%m-%d %H:%M') if obj.ready_at else '—',
            obj.delivered_at.strftime('%Y-%m-%d %H:%M') if obj.delivered_at else '—',
            obj.paid_at.strftime('%Y-%m-%d %H:%M') if obj.paid_at else '—',
        )
    order_timeline.short_description = _('Timeline')
    
    def mark_confirmed(self, request, queryset):
        """Mark orders as confirmed."""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_confirmed.short_description = _('✓ Mark as confirmed')
    
    def mark_ready(self, request, queryset):
        """Mark orders as ready."""
        from django.utils import timezone
        updated = 0
        for order in queryset.filter(status='confirmed'):
            order.status = 'ready'
            order.ready_at = timezone.now()
            order.save()
            updated += 1
        self.message_user(request, f'{updated} orders marked as ready.')
    mark_ready.short_description = _('🍽️ Mark as ready')
    
    def mark_delivered(self, request, queryset):
        """Mark orders as delivered."""
        from django.utils import timezone
        updated = 0
        for order in queryset.filter(status='ready'):
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
            updated += 1
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = _('📦 Mark as delivered')
    
    def mark_paid(self, request, queryset):
        """Mark orders as paid."""
        from django.utils import timezone
        updated = 0
        for order in queryset.filter(status='delivered'):
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            updated += 1
        self.message_user(request, f'{updated} orders marked as paid.')
    mark_paid.short_description = _('💳 Mark as paid')
    
    def table(self, obj):
        return obj.table_session.table
    table.short_description = _('Столик')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(table_session__table__restaurant=request.user.restaurant)
        if request.user.is_waiter:
            return qs.filter(table_session__table__restaurant=request.user.restaurant)
        return qs.none()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model."""
    
    list_display = ['id', 'order', 'menu_item', 'quantity', 'price']
    list_filter = ['order__created_at', 'order__table_session__table__restaurant']
    search_fields = ['menu_item__name', 'order__id']
    ordering = ['-order__created_at']
    readonly_fields = ('order', 'menu_item', 'quantity', 'price')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner or request.user.is_waiter:
            return qs.filter(order__table_session__table__restaurant=request.user.restaurant)
        return qs.none()
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
