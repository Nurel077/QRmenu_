"""
Serializers for menu app.
"""
from rest_framework import serializers
from .models import MenuCategory, MenuItem


class MenuCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for MenuCategory model.
    """
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MenuCategory
        fields = (
            'id', 'restaurant', 'name', 'description', 'icon',
            'order', 'is_active', 'items_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class MenuItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing menu items.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = (
            'id', 'category', 'category_name', 'name', 'price', 'image',
            'is_vegetarian', 'is_vegan', 'is_spicy', 'spicy_level',
            'is_chef_special', 'is_popular', 'is_available', 'order'
        )
        read_only_fields = ('id',)


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for menu item details.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = (
            'id', 'category', 'category_name', 'name', 'description', 'image',
            'price', 'cooking_time', 'calories', 'weight', 'is_vegetarian',
            'is_vegan', 'is_spicy', 'spicy_level', 'is_chef_special',
            'is_popular', 'allergens', 'is_available', 'stock_quantity',
            'order', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class MenuItemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating menu items.
    """
    class Meta:
        model = MenuItem
        fields = (
            'category', 'name', 'description', 'image', 'price',
            'cooking_time', 'calories', 'weight', 'is_vegetarian',
            'is_vegan', 'is_spicy', 'spicy_level', 'is_chef_special',
            'is_popular', 'allergens', 'is_available', 'stock_quantity', 'order'
        )
