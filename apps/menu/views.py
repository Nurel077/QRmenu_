"""
Views and ViewSets for menu app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MenuCategory, MenuItem
from .serializers import (
    MenuCategorySerializer, MenuItemListSerializer,
    MenuItemDetailSerializer, MenuItemCreateUpdateSerializer
)


class MenuCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for menu categories.
    """
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['restaurant', 'is_active']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        user = self.request.user
        queryset = MenuCategory.objects.all()
        
        if not user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        restaurant_slug = self.request.query_params.get('restaurant_slug')
        if restaurant_slug:
            queryset = queryset.filter(restaurant__slug=restaurant_slug)
        
        return queryset


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for menu items.
    """
    queryset = MenuItem.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_available', 'is_vegetarian', 'is_vegan', 'is_spicy']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'order', 'name']
    ordering = ['order', 'name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MenuItemDetailSerializer
        elif self.action == 'list':
            return MenuItemListSerializer
        else:
            return MenuItemCreateUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = MenuItem.objects.all()
        
        if not user.is_authenticated:
            queryset = queryset.filter(is_available=True)
        
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        restaurant_slug = self.request.query_params.get('restaurant_slug')
        if restaurant_slug:
            queryset = queryset.filter(category__restaurant__slug=restaurant_slug)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular menu items"""
        items = self.get_queryset().filter(is_popular=True)[:10]
        serializer = MenuItemListSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def chef_special(self, request):
        """Get chef's special items"""
        items = self.get_queryset().filter(is_chef_special=True)
        serializer = MenuItemListSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vegetarian(self, request):
        """Get vegetarian items"""
        items = self.get_queryset().filter(is_vegetarian=True)
        serializer = MenuItemListSerializer(items, many=True)
        return Response(serializer.data)
