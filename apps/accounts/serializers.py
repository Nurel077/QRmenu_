"""
Serializers for accounts app.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import GuestSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'role_display', 'restaurant', 'restaurant_name',
            'avatar', 'is_active_waiter', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_superuser', 'is_staff')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role'
        )
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Пароли не совпадают.'})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    """
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'avatar'
        )
        read_only_fields = ('id', 'username')


class GuestSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for GuestSession model.
    """
    table_number = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = GuestSession
        fields = (
            'id', 'session_key', 'guest_name', 'table_session',
            'table_number', 'restaurant_name', 'created_at', 'last_activity'
        )
        read_only_fields = ('id', 'session_key', 'created_at', 'last_activity')
    
    @extend_schema_field(serializers.CharField())
    def get_table_number(self, obj):
        return obj.table_session.table.number
    
    @extend_schema_field(serializers.CharField())
    def get_restaurant_name(self, obj):
        return obj.table_session.table.restaurant.name


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Пароли не совпадают.'})
        return data
