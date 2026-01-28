"""
Serializers for tables app.
"""
from rest_framework import serializers
from .models import Table, TableSession


class TableSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for TableSession model.
    """
    table_number = serializers.CharField(source='table.number', read_only=True)
    restaurant_name = serializers.CharField(source='table.restaurant.name', read_only=True)
    guests_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TableSession
        fields = (
            'id', 'table', 'table_number', 'restaurant_name', 'guests_count',
            'session_code', 'started_at', 'closed_at'
        )
        read_only_fields = ('id', 'session_code', 'started_at', 'closed_at')


class TableListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tables.
    """
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    current_session = TableSessionSerializer(read_only=True)
    current_orders_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Table
        fields = (
            'id', 'restaurant', 'restaurant_name', 'number', 'capacity',
            'is_occupied', 'is_active', 'zone', 'current_session',
            'current_orders_count'
        )
        read_only_fields = ('id', 'current_session', 'current_orders_count')


class TableDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for table details.
    """
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    current_session = TableSessionSerializer(read_only=True)
    current_orders_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Table
        fields = (
            'id', 'restaurant', 'restaurant_name', 'number', 'capacity',
            'qr_code', 'qr_url', 'is_occupied', 'is_active', 'zone',
            'description', 'current_session', 'current_orders_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'qr_code', 'qr_url', 'created_at', 'updated_at')


class TableCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating tables.
    """
    class Meta:
        model = Table
        fields = (
            'number', 'capacity', 'is_active', 'zone', 'description'
        )
