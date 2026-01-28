"""
Views and ViewSets for orders app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer,
    OrderCreateSerializer, OrderUpdateSerializer,
    OrderItemSerializer
)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order items.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['order', 'menu_item']


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for orders.
    """
    queryset = Order.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['table_session', 'status', 'payment_method']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        else:
            return OrderUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all()
        
        restaurant_slug = self.request.query_params.get('restaurant_slug')
        if restaurant_slug:
            queryset = queryset.filter(table_session__table__restaurant__slug=restaurant_slug)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm order by waiter"""
        order = self.get_object()
        
        if order.status != Order.Status.PENDING:
            return Response(
                {'error': 'Заказ уже был подтвержден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.confirm_order(request.user)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_ready(self, request, pk=None):
        """Mark order as ready"""
        order = self.get_object()
        
        if order.status not in [Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.PREPARING]:
            return Response(
                {'error': 'Не может быть отмечено как готово'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        order.status = Order.Status.READY
        order.ready_at = timezone.now()
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark order as delivered"""
        order = self.get_object()
        
        from django.utils import timezone
        order.status = Order.Status.DELIVERED
        order.delivered_at = timezone.now()
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark order as paid"""
        order = self.get_object()
        
        from django.utils import timezone
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        if order.status in [Order.Status.PAID, Order.Status.DELIVERED]:
            return Response(
                {'error': 'Не может быть отменен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active orders"""
        orders = self.get_queryset().exclude(status__in=[Order.Status.PAID, Order.Status.CANCELLED])
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders"""
        orders = self.get_queryset().filter(status=Order.Status.PENDING)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
