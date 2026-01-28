"""
Serializers for orders app.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    item_name = serializers.CharField(source='menu_item.name', read_only=True)
    item_price = serializers.DecimalField(source='menu_item.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'order', 'menu_item', 'item_name', 'quantity',
            'price', 'item_price'
        )
        read_only_fields = ('id',)


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing orders.
    """
    table_number = serializers.CharField(source='table_session.table.number', read_only=True)
    guest_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Order
        fields = (
            'id', 'table_number', 'guest_info', 'status', 'status_display',
            'payment_method', 'payment_method_display', 'items_count',
            'total_amount', 'created_at', 'paid_at'
        )
        read_only_fields = ('id', 'items_count', 'total_amount', 'created_at', 'paid_at')
    
    @extend_schema_field(serializers.CharField())
    def get_guest_info(self, obj):
        if obj.guest_name:
            return obj.guest_name
        if obj.guest_session and obj.guest_session.guest_name:
            return obj.guest_session.guest_name
        return 'Аноним'


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for order details.
    """
    items = OrderItemSerializer(read_only=True, many=True)
    table_number = serializers.CharField(source='table_session.table.number', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    waiter_name = serializers.CharField(source='waiter.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    service_charge_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'table_number', 'restaurant_name', 'guest_name', 'waiter',
            'waiter_name', 'status', 'status_display', 'payment_method',
            'payment_method_display', 'notes', 'waiter_notes', 'items',
            'subtotal', 'tax_amount', 'service_charge_amount', 'total_amount',
            'items_count', 'created_at', 'confirmed_at', 'ready_at',
            'delivered_at', 'paid_at', 'cancelled_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'subtotal', 'tax_amount', 'service_charge_amount',
            'total_amount', 'items_count', 'created_at', 'confirmed_at',
            'ready_at', 'delivered_at', 'paid_at', 'cancelled_at', 'updated_at'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating orders.
    """
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Order
        fields = (
            'table_session', 'guest_name', 'payment_method', 'notes', 'items_data'
        )
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating orders.
    """
    class Meta:
        model = Order
        fields = (
            'status', 'payment_method', 'notes', 'waiter_notes'
        )
