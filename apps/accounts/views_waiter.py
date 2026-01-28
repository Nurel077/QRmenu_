"""
Views for waiter panel.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.orders.models import Order
from apps.orders.serializers import OrderDetailSerializer
from apps.accounts.permissions import IsWaiter


class WaiterLoginView(LoginView):
    """Custom login view for waiters."""
    template_name = 'waiter/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('waiter:dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_waiter:
            # Show error if not a waiter
            return self.form_invalid(form)
        return super().form_valid(form)


@login_required(login_url='waiter:login')
def waiter_dashboard(request):
    """Waiter dashboard view."""
    if not request.user.is_waiter:
        return render(request, 'waiter/unauthorized.html', {'error': 'Access denied. Waiter role required.'}, status=403)
    
    context = {
        'user': request.user,
    }
    return render(request, 'waiter/dashboard.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsWaiter])
def waiter_orders(request):
    """Get orders for waiter."""
    restaurant = request.user.restaurant
    
    # Get query parameters for filtering
    status = request.query_params.get('status')
    
    queryset = Order.objects.filter(
        table_session__table__restaurant=restaurant
    ).select_related('table_session', 'guest_session')
    
    if status:
        statuses = status.split(',')
        queryset = queryset.filter(status__in=statuses)
    
    serializer = OrderDetailSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsWaiter])
def waiter_tasks(request):
    """Get waiter's pending tasks."""
    restaurant = request.user.restaurant
    waiter = request.user
    
    # Orders for this waiter or restaurant
    pending_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status__in=['pending', 'confirmed']
    ).select_related('table_session', 'guest_session').count()
    
    # Ready orders waiting for pickup
    ready_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status='ready'
    ).count()
    
    return Response({
        'pending_orders': pending_orders,
        'ready_for_pickup': ready_orders,
        'total_tasks': pending_orders + ready_orders,
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsWaiter])
def update_order(request, order_id):
    """Update order status."""
    try:
        order = Order.objects.get(id=order_id)
        restaurant = request.user.restaurant
        
        # Check if waiter can update this order
        if order.table_session.table.restaurant != restaurant:
            return Response({'error': 'Not authorized'}, status=403)
        
        # Update status
        if 'status' in request.data:
            order.status = request.data['status']
            order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsWaiter])
def restaurant_statistics(request):
    """Get restaurant statistics for waiter."""
    restaurant = request.user.restaurant
    
    total_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant
    ).count()
    
    pending_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status='pending'
    ).count()
    
    confirmed_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status='confirmed'
    ).count()
    
    ready_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status='ready'
    ).count()
    
    delivered_orders = Order.objects.filter(
        table_session__table__restaurant=restaurant,
        status='delivered'
    ).count()
    
    return Response({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'ready_orders': ready_orders,
        'delivered_orders': delivered_orders,
    })
