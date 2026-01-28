"""
Admin configuration for tables app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Table, TableSession


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Table model."""
    
    list_display = ['number_link', 'restaurant', 'capacity_display', 'zone_badge', 'status_badge', 
                    'current_orders_count', 'qr_code_preview']
    list_filter = ['is_active', 'is_occupied', 'zone', 'restaurant', 'created_at']
    search_fields = ['number', 'restaurant__name', 'zone']
    ordering = ['restaurant', 'number']
    readonly_fields = ('qr_code', 'qr_url', 'current_orders_count', 'created_at', 'updated_at', 'qr_code_preview')
    actions = ['occupy_tables', 'release_tables', 'activate_tables', 'deactivate_tables']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('restaurant', 'number', 'capacity', 'zone', 'description')
        }),
        (_('QR код'), {
            'fields': ('qr_code', 'qr_url', 'qr_code_preview'),
        }),
        (_('Статус'), {
            'fields': ('is_active', 'is_occupied')
        }),
        (_('Статистика'), {
            'fields': ('current_orders_count',),
            'classes': ('collapse',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def number_link(self, obj):
        """Display table number with link."""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:tables_table_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, f'Table {obj.number}')
    number_link.short_description = _('Table')
    
    def capacity_display(self, obj):
        """Display capacity with seat icons."""
        from django.utils.html import format_html
        return format_html('👥 {}', obj.capacity)
    capacity_display.short_description = _('Capacity')
    
    def zone_badge(self, obj):
        """Display zone badge."""
        from django.utils.html import format_html
        colors = {'A': '#007bff', 'B': '#28a745', 'C': '#ffc107', 'D': '#dc3545'}
        color = colors.get(obj.zone, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.zone or '—'
        )
    zone_badge.short_description = _('Zone')
    
    def status_badge(self, obj):
        """Display table status badge."""
        from django.utils.html import format_html
        if obj.is_occupied:
            status = '🔴 Occupied'
            color = '#dc3545'
        else:
            status = '🟢 Free'
            color = '#28a745'
        
        active = 'Active' if obj.is_active else 'Inactive'
        active_color = 'green' if obj.is_active else 'red'
        
        return format_html(
            '<span style="color: {};"><strong>{}</strong></span><br><span style="color: {}; font-size: 0.8em;">{}</span>',
            color, status, active_color, active
        )
    status_badge.short_description = _('Status')
    
    def qr_code_preview(self, obj):
        """Display QR code preview."""
        from django.utils.html import format_html
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px;" />',
                obj.qr_code.url
            )
        return '—'
    qr_code_preview.short_description = _('QR Code')
    
    def occupy_tables(self, request, queryset):
        """Mark tables as occupied."""
        updated = queryset.update(is_occupied=True)
        self.message_user(request, f'{updated} tables marked as occupied.')
    occupy_tables.short_description = _('Mark as occupied')
    
    def release_tables(self, request, queryset):
        """Mark tables as free."""
        updated = queryset.update(is_occupied=False)
        self.message_user(request, f'{updated} tables marked as free.')
    release_tables.short_description = _('Mark as free')
    
    def activate_tables(self, request, queryset):
        """Activate tables."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} tables activated.')
    activate_tables.short_description = _('Activate tables')
    
    def deactivate_tables(self, request, queryset):
        """Deactivate tables."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} tables deactivated.')
    deactivate_tables.short_description = _('Deactivate tables')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(restaurant=request.user.restaurant)
        return qs.none()


@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin):
    """Admin interface for TableSession model."""
    
    list_display = ['id', 'table', 'guests_count', 'started_at', 'closed_at', 'is_active']
    list_filter = ['started_at', 'closed_at', 'table__restaurant']
    search_fields = ['table__number', 'table__restaurant__name', 'session_code']
    ordering = ['-started_at']
    readonly_fields = ('session_code', 'started_at', 'closed_at')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('table', 'waiter', 'session_code')
        }),
        (_('Время'), {
            'fields': ('started_at', 'closed_at')
        }),
        (_('Заметки'), {
            'fields': ('notes',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(table__restaurant=request.user.restaurant)
        return qs.none()
    
    def is_active(self, obj):
        return obj.closed_at is None
    is_active.boolean = True
    is_active.short_description = 'Активна'
