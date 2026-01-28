"""
Enhanced admin configuration for menu app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import MenuCategory, MenuItem


class MenuItemInline(admin.TabularInline):
    """Inline admin for menu items within categories."""
    model = MenuItem
    extra = 0
    fields = ['name', 'price', 'is_available', 'is_chef_special', 'is_popular', 'order']
    ordering = ['order']


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    """Enhanced admin for MenuCategory."""
    
    list_display = ['name', 'restaurant', 'items_count_display', 'is_active_badge', 'order', 'created_at']
    list_filter = ['is_active', 'restaurant', 'created_at']
    search_fields = ['name', 'restaurant__name']
    ordering = ['restaurant', 'order']
    readonly_fields = ['created_at', 'updated_at', 'items_count']
    inlines = [MenuItemInline]
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('restaurant', 'name', 'description', 'icon')
        }),
        (_('Параметры'), {
            'fields': ('order', 'is_active')
        }),
        (_('Статистика'), {
            'fields': ('items_count',),
            'classes': ('collapse',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def items_count_display(self, obj):
        """Display number of items in category."""
        count = obj.items_count
        color = 'green' if count > 0 else 'orange'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} items</span>',
            color,
            count
        )
    items_count_display.short_description = _('Items')
    
    def is_active_badge(self, obj):
        """Display active status badge."""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = _('Status')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(restaurant=request.user.restaurant)
        return qs.none()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Enhanced admin for MenuItem."""
    
    list_display = ['name', 'category', 'price_display', 'tags_display', 'availability_badge', 'image_preview', 'order']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_vegan', 'is_spicy', 'is_chef_special', 'is_popular', 'category__restaurant']
    search_fields = ['name', 'description', 'category__name']
    ordering = ['category', 'order']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large', 'tags_list']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('category', 'name', 'description', 'price')
        }),
        (_('Изображение'), {
            'fields': ('image', 'image_preview_large')
        }),
        (_('Характеристики'), {
            'fields': ('is_vegetarian', 'is_vegan', 'is_spicy', 'spicy_level'),
            'description': _('Отметьте характеристики блюда')
        }),
        (_('Специальные статусы'), {
            'fields': ('is_chef_special', 'is_popular'),
            'description': _('Блюдо дня или популярное блюдо')
        }),
        (_('Дополнительная информация'), {
            'fields': ('cooking_time', 'calories', 'weight', 'allergens'),
            'classes': ('collapse',)
        }),
        (_('Наличие и статус'), {
            'fields': ('is_available', 'stock_quantity')
        }),
        (_('Сортировка'), {
            'fields': ('order',)
        }),
        (_('Теги и метаданные'), {
            'fields': ('tags_list',),
            'classes': ('collapse',)
        }),
        (_('Важные даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display price with currency."""
        return format_html(
            '<span style="font-weight: bold; color: green;">${}</span>',
            obj.price
        )
    price_display.short_description = _('Price')
    
    def tags_display(self, obj):
        """Display item tags/characteristics."""
        tags = obj.get_tags()
        if not tags:
            return '—'
        
        html_tags = ' '.join([
            f'<span style="background-color: #e7f3ff; color: #0066cc; padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 0.8em;">{tag}</span>'
            for tag in tags
        ])
        return format_html(html_tags)
    tags_display.short_description = _('Tags')
    
    def tags_list(self, obj):
        """Display tags list in detail view."""
        tags = obj.get_tags()
        if not tags:
            return _('No tags')
        return ', '.join(tags)
    tags_list.short_description = _('Tags')
    
    def availability_badge(self, obj):
        """Display availability status."""
        if obj.is_available:
            if obj.stock_quantity is None:
                return format_html('<span style="color: green;">✓ In Stock (Unlimited)</span>')
            elif obj.stock_quantity > 0:
                return format_html(
                    '<span style="color: green;">✓ In Stock ({})</span>',
                    obj.stock_quantity
                )
            else:
                return format_html('<span style="color: orange;">⚠ Out of Stock</span>')
        return format_html('<span style="color: red;">✗ Not Available</span>')
    availability_badge.short_description = _('Availability')
    
    def image_preview(self, obj):
        """Display small image preview in list."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 3px; object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = _('Image')
    
    def image_preview_large(self, obj):
        """Display large image preview in detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 5px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview_large.short_description = _('Image Preview')
    
    actions = ['make_available', 'make_unavailable', 'set_chef_special', 'unset_chef_special']
    
    def make_available(self, request, queryset):
        """Make items available."""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} items marked as available.')
    make_available.short_description = _('Mark selected items as available')
    
    def make_unavailable(self, request, queryset):
        """Make items unavailable."""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} items marked as unavailable.')
    make_unavailable.short_description = _('Mark selected items as unavailable')
    
    def set_chef_special(self, request, queryset):
        """Mark as chef special."""
        updated = queryset.update(is_chef_special=True)
        self.message_user(request, f'{updated} items marked as chef special.')
    set_chef_special.short_description = _('Mark as chef special')
    
    def unset_chef_special(self, request, queryset):
        """Unmark chef special."""
        updated = queryset.update(is_chef_special=False)
        self.message_user(request, f'{updated} items unmarked from chef special.')
    unset_chef_special.short_description = _('Remove chef special mark')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_owner:
            return qs.filter(category__restaurant=request.user.restaurant)
        return qs.none()
