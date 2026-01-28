"""
Views and ViewSets for payments app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Payment
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payments.
    """
    queryset = Payment.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'order', 'table_session']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        else:
            return PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.all()
        
        restaurant_slug = self.request.query_params.get('restaurant_slug')
        if restaurant_slug:
            queryset = queryset.filter(
                order__table_session__table__restaurant__slug=restaurant_slug
            ) | queryset.filter(
                table_session__table__restaurant__slug=restaurant_slug
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm payment"""
        payment = self.get_object()
        
        if payment.status != Payment.Status.PENDING:
            return Response(
                {'error': 'Платеж уже был обработан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = Payment.Status.COMPLETED
        payment.save()
        
        # Update order status if exists
        if payment.order:
            payment.order.status = 'paid'
            payment.order.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject payment"""
        payment = self.get_object()
        
        if payment.status != Payment.Status.PENDING:
            return Response(
                {'error': 'Платеж уже был обработан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = Payment.Status.FAILED
        payment.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund payment"""
        payment = self.get_object()
        
        if payment.status != Payment.Status.COMPLETED:
            return Response(
                {'error': 'Только завершенные платежи могут быть возвращены'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = Payment.Status.REFUNDED
        payment.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending payments"""
        payments = self.get_queryset().filter(status=Payment.Status.PENDING)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payment statistics"""
        from django.db.models import Sum, Count
        from datetime import timedelta
        from django.utils import timezone
        
        restaurant_slug = request.query_params.get('restaurant_slug')
        
        queryset = self.get_queryset()
        
        total_revenue = queryset.filter(status=Payment.Status.COMPLETED).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        today_revenue = queryset.filter(
            status=Payment.Status.COMPLETED,
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        payment_methods = queryset.values('payment_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        return Response({
            'total_revenue': total_revenue,
            'today_revenue': today_revenue,
            'payment_methods': payment_methods,
            'total_transactions': queryset.count(),
            'pending_transactions': queryset.filter(status=Payment.Status.PENDING).count()
        })
