"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import User, GuestSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced admin interface for User model."""
    
    list_display = ['username_link', 'email', 'role_badge', 'restaurant', 'status_badge', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'restaurant', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined', 'user_avatar']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'user_avatar')
        }),
        (_('Роль и привязка'), {
            'fields': ('role', 'restaurant', 'is_active_waiter')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'restaurant'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'set_waiter_active', 'set_waiter_inactive']
    
    def username_link(self, obj):
        """Display username with link."""
        url = reverse('admin:accounts_user_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.username)
    username_link.short_description = _('Username')
    
    def role_badge(self, obj):
        """Display role with color badge."""
        colors = {
            'owner': '#28a745',
            'waiter': '#007bff',
            'guest': '#6c757d',
            'admin': '#dc3545',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = _('Role')
    
    def status_badge(self, obj):
        """Display active status with badge."""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Inactive</span>'
            )
    status_badge.short_description = _('Status')
    
    def user_avatar(self, obj):
        """Display user avatar."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px;" />',
                obj.avatar.url
            )
        return _('No avatar')
    user_avatar.short_description = _('Avatar Preview')
    
    def activate_users(self, request, queryset):
        """Activate selected users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = _('Activate selected users')
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = _('Deactivate selected users')
    
    def set_waiter_active(self, request, queryset):
        """Set waiters as active."""
        updated = queryset.filter(role='waiter').update(is_active_waiter=True)
        self.message_user(request, f'{updated} waiters activated.')
    set_waiter_active.short_description = _('Activate selected waiters')
    
    def set_waiter_inactive(self, request, queryset):
        """Set waiters as inactive."""
        updated = queryset.filter(role='waiter').update(is_active_waiter=False)
        self.message_user(request, f'{updated} waiters deactivated.')
    set_waiter_inactive.short_description = _('Deactivate selected waiters')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Владельцы видят только сотрудников своего ресторана
        if request.user.is_owner:
            return qs.filter(restaurant=request.user.restaurant)
        return qs.none()


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    """Admin interface for GuestSession model."""
    
    list_display = ['session_key', 'table_link', 'restaurant', 'guest_name', 'session_status', 'duration']
    list_filter = ['table_session__table__restaurant', 'created_at']
    search_fields = ['session_key', 'guest_name', 'table_session__session_code']
    readonly_fields = ['session_key', 'created_at', 'last_activity', 'session_details']
    
    fieldsets = (
        (_('Session Info'), {
            'fields': ('session_key', 'guest_name', 'table_session', 'session_details')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def table_link(self, obj):
        """Display table with link."""
        table = obj.table_session.table
        url = reverse('admin:tables_table_change', args=[table.id])
        return format_html('<a href="{}">{}</a>', url, table.number)
    table_link.short_description = _('Table')
    
    def restaurant(self, obj):
        """Display restaurant name."""
        return obj.table_session.table.restaurant.name
    restaurant.short_description = _('Restaurant')
    
    def session_status(self, obj):
        """Display session status badge."""
        status = 'Active' if not obj.created_at else 'Completed'
        color = 'green' if not obj.created_at else 'gray'
        return format_html(
            '<span style="color: {};">● {}</span>',
            color,
            status
        )
    session_status.short_description = _('Status')
    
    def duration(self, obj):
        """Display session duration."""
        from django.utils import timezone
        if obj.created_at:
            duration = timezone.now() - obj.created_at
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f'{hours}h {minutes}m'
        return '—'
    duration.short_description = _('Duration')
    
    def session_details(self, obj):
        """Display detailed session information."""
        return format_html(
            '<strong>Session Key:</strong> {}<br>'
            '<strong>Guest:</strong> {}<br>'
            '<strong>Table:</strong> {}<br>'
            '<strong>Restaurant:</strong> {}<br>',
            obj.session_key,
            obj.guest_name or 'Unknown',
            obj.table_session.table.number,
            obj.table_session.table.restaurant.name
        )
    session_details.short_description = _('Details')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(table_session__table__restaurant=request.user.restaurant)
        return qs.none()
