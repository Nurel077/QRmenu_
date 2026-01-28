"""
Serializers for payments app.
"""
import uuid
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    """
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    table_number = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'payment_id', 'order', 'order_id', 'table_session',
            'payment_type', 'payment_type_display', 'status', 'status_display',
            'amount', 'currency', 'payer_name', 'payer_phone', 'payer_email',
            'table_number', 'restaurant_name', 'transaction_id',
            'notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'payment_id', 'created_at', 'updated_at')
    
    @extend_schema_field(serializers.CharField())
    def get_table_number(self, obj):
        if obj.table_session:
            return obj.table_session.table.number
        elif obj.order:
            return obj.order.table_session.table.number
        return None
    
    @extend_schema_field(serializers.CharField())
    def get_restaurant_name(self, obj):
        if obj.table_session:
            return obj.table_session.table.restaurant.name
        elif obj.order:
            return obj.order.restaurant.name
        return None


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments.
    """
    class Meta:
        model = Payment
        fields = (
            'order', 'table_session', 'payment_type', 'amount',
            'payer_name', 'payer_phone', 'payer_email', 'notes'
        )
    
    def create(self, validated_data):
        validated_data['payment_id'] = str(uuid.uuid4())
        return super().create(validated_data)


class PaymentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating payments.
    """
    class Meta:
        model = Payment
        fields = (
            'status', 'transaction_id', 'notes'
        )
