"""
Views and ViewSets for tables app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Table, TableSession
from .serializers import (
    TableListSerializer, TableDetailSerializer,
    TableCreateUpdateSerializer, TableSessionSerializer
)


class TableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tables.
    """
    queryset = Table.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['restaurant', 'is_active', 'zone']
    ordering_fields = ['number', 'capacity']
    ordering = ['number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TableDetailSerializer
        elif self.action == 'list':
            return TableListSerializer
        else:
            return TableCreateUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Table.objects.all()
        
        restaurant_slug = self.request.query_params.get('restaurant_slug')
        if restaurant_slug:
            queryset = queryset.filter(restaurant__slug=restaurant_slug)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def open_session(self, request, pk=None):
        """Open new table session"""
        table = self.get_object()
        
        if table.is_occupied:
            return Response(
                {'error': 'Столик уже занят'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = TableSession.objects.create(table=table)
        serializer = TableSessionSerializer(session)
        
        table.is_occupied = True
        table.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def current_session(self, request, pk=None):
        """Get current table session"""
        table = self.get_object()
        session = table.current_session
        
        if not session:
            return Response(
                {'error': 'Нет активной сессии'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TableSessionSerializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close_session(self, request, pk=None):
        """Close table session"""
        table = self.get_object()
        session = table.current_session
        
        if not session:
            return Response(
                {'error': 'Нет активной сессии'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.utils import timezone
        session.closed_at = timezone.now()
        session.save()
        
        table.is_occupied = False
        table.save()
        
        serializer = TableSessionSerializer(session)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available tables"""
        tables = self.get_queryset().filter(is_active=True, is_occupied=False)
        serializer = TableListSerializer(tables, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def occupied(self, request):
        """Get occupied tables"""
        tables = self.get_queryset().filter(is_occupied=True)
        serializer = TableListSerializer(tables, many=True)
        return Response(serializer.data)


class TableSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for table sessions (read-only).
    """
    queryset = TableSession.objects.all()
    serializer_class = TableSessionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['table', 'table__restaurant']
    ordering_fields = ['opened_at']
    ordering = ['-opened_at']
