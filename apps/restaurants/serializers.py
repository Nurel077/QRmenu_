"""
Serializers for restaurants app.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Restaurant, RestaurantSettings


class RestaurantSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for RestaurantSettings model.
    """
    class Meta:
        model = RestaurantSettings
        fields = (
            'id', 'restaurant', 'email_notifications', 'sms_notifications',
            'primary_color', 'secondary_color', 'welcome_message', 'footer_text'
        )
        read_only_fields = ('id', 'restaurant')


class RestaurantListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing restaurants with minimal info.
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    total_tables = serializers.SerializerMethodField()
    active_tables = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'slug', 'owner', 'owner_name', 'logo',
            'city', 'phone', 'is_active', 'total_tables', 'active_tables'
        )
        read_only_fields = ('id', 'slug')
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_tables(self, obj):
        return obj.total_tables
    
    @extend_schema_field(serializers.IntegerField())
    def get_active_tables(self, obj):
        return obj.active_tables


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for restaurant details.
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    settings = RestaurantSettingsSerializer(read_only=True)
    total_tables = serializers.SerializerMethodField()
    active_tables = serializers.SerializerMethodField()
    is_open_now = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'slug', 'owner', 'owner_name', 'description',
            'logo', 'cover_image', 'phone', 'email', 'website', 'address',
            'city', 'country', 'currency', 'language', 'tax_rate',
            'service_charge', 'opening_time', 'closing_time', 'is_active',
            'allow_cash_payment', 'allow_qr_payment', 'require_waiter_confirmation',
            'settings', 'is_open_now', 'total_tables', 'active_tables',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_tables(self, obj):
        return obj.total_tables
    
    @extend_schema_field(serializers.IntegerField())
    def get_active_tables(self, obj):
        return obj.active_tables


class RestaurantCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating restaurants.
    """
    class Meta:
        model = Restaurant
        fields = (
            'name', 'description', 'logo', 'cover_image', 'phone', 'email',
            'website', 'address', 'city', 'country', 'currency', 'language',
            'tax_rate', 'service_charge', 'opening_time', 'closing_time',
            'is_active', 'allow_cash_payment', 'allow_qr_payment',
            'require_waiter_confirmation'
        )
    
    def create(self, validated_data):
        # Set the owner from request context
        if 'request' in self.context:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)