"""
Admin configuration for restaurants app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import Restaurant, RestaurantSettings


class RestaurantSettingsInline(admin.TabularInline):
    """Inline admin for RestaurantSettings with enhanced display."""
    model = RestaurantSettings
    extra = 0
    fields = ('email_notifications', 'sms_notifications', 'primary_color', 'secondary_color')


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    """Enhanced admin for RestaurantSettings."""
    
    list_display = ['restaurant', 'notifications_status', 'colors_preview', 'modified_date']
    list_filter = ['email_notifications', 'sms_notifications']
    search_fields = ['restaurant__name']
    readonly_fields = ['restaurant', 'color_preview']
    
    def notifications_status(self, obj):
        """Display notification preferences."""
        email = '✓ Email' if obj.email_notifications else '✗ Email'
        sms = '✓ SMS' if obj.sms_notifications else '✗ SMS'
        return format_html('{}<br>{}', email, sms)
    notifications_status.short_description = _('Notifications')
    
    def colors_preview(self, obj):
        """Display color preview."""
        return format_html(
            '<div style="display: flex; gap: 10px;">'
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">Primary</span>'
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">Secondary</span>'
            '</div>',
            obj.primary_color,
            obj.secondary_color
        )
    colors_preview.short_description = _('Colors')
    
    def color_preview(self, obj):
        """Display detailed color preview."""
        return format_html(
            '<div style="display: flex; gap: 20px; align-items: center;">'
            '<div><strong>Primary:</strong><br><span style="background-color: {}; padding: 10px 20px; display: inline-block; border-radius: 5px; color: white;">Sample Text</span></div>'
            '<div><strong>Secondary:</strong><br><span style="background-color: {}; padding: 10px 20px; display: inline-block; border-radius: 5px; color: white;">Sample Text</span></div>'
            '</div>',
            obj.primary_color,
            obj.secondary_color
        )
    color_preview.short_description = _('Color Preview')
    
    def modified_date(self, obj):
        """Display last modified date."""
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    modified_date.short_description = _('Last Modified')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Restaurant model."""
    
    list_display = ['name_link', 'owner', 'city', 'status_badge', 'stats_display', 'created_at']
    list_filter = ['is_active', 'city', 'country', 'created_at', 'allow_cash_payment', 'allow_qr_payment']
    search_fields = ['name', 'owner__username', 'phone', 'email', 'address']
    ordering = ['-created_at']
    readonly_fields = ('slug', 'total_tables', 'active_tables', 'created_at', 'updated_at', 'logo_preview', 'cover_preview', 'stats_info')
    inlines = [RestaurantSettingsInline]
    actions = ['activate_restaurants', 'deactivate_restaurants', 'enable_cash', 'disable_cash']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'owner', 'description')
        }),
        (_('Изображения'), {
            'fields': ('logo', 'logo_preview', 'cover_image', 'cover_preview')
        }),
        (_('Контактная информация'), {
            'fields': ('phone', 'email', 'website')
        }),
        (_('Адрес'), {
            'fields': ('address', 'city', 'country')
        }),
        (_('Настройки и параметры'), {
            'fields': ('currency', 'language', 'tax_rate', 'service_charge',
                       'opening_time', 'closing_time')
        }),
        (_('Методы оплаты'), {
            'fields': ('allow_cash_payment', 'allow_qr_payment', 'require_waiter_confirmation')
        }),
        (_('Статус'), {
            'fields': ('is_active',)
        }),
        (_('Статистика'), {
            'fields': ('stats_info',),
            'classes': ('collapse',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_link(self, obj):
        """Display restaurant name with link."""
        url = reverse('admin:restaurants_restaurant_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.name)
    name_link.short_description = _('Name')
    
    def status_badge(self, obj):
        """Display active status badge."""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    status_badge.short_description = _('Status')
    
    def stats_display(self, obj):
        """Display quick statistics."""
        return format_html(
            '🪑 {} | 📋 {}',
            obj.total_tables,
            obj.active_tables
        )
    stats_display.short_description = _('Stats')
    
    def stats_info(self, obj):
        """Display detailed statistics."""
        return format_html(
            '<strong>Total Tables:</strong> {}<br>'
            '<strong>Active Tables:</strong> {}<br>'
            '<strong>Is Open Now:</strong> {}',
            obj.total_tables,
            obj.active_tables,
            '✓ Yes' if obj.is_open_now else '✗ No'
        )
    
    def logo_preview(self, obj):
        """Display logo preview."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 5px;" />',
                obj.logo.url
            )
        return _('No logo')
    logo_preview.short_description = _('Logo Preview')
    
    def cover_preview(self, obj):
        """Display cover image preview."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 5px;" />',
                obj.cover_image.url
            )
        return _('No cover image')
    cover_preview.short_description = _('Cover Preview')
    
    def activate_restaurants(self, request, queryset):
        """Activate selected restaurants."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} restaurants activated.')
    activate_restaurants.short_description = _('Activate selected restaurants')
    
    def deactivate_restaurants(self, request, queryset):
        """Deactivate selected restaurants."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} restaurants deactivated.')
    deactivate_restaurants.short_description = _('Deactivate selected restaurants')
    
    def enable_cash(self, request, queryset):
        """Enable cash payments."""
        updated = queryset.update(allow_cash_payment=True)
        self.message_user(request, f'Cash enabled for {updated} restaurants.')
    enable_cash.short_description = _('Enable cash payment')
    
    def disable_cash(self, request, queryset):
        """Disable cash payments."""
        updated = queryset.update(allow_cash_payment=False)
        self.message_user(request, f'Cash disabled for {updated} restaurants.')
    disable_cash.short_description = _('Disable cash payment')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(owner=request.user)
        return qs.none()
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_owner
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.owner:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.owner:
            return True
        return False
