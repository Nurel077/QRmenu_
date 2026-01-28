"""
Views and ViewSets for restaurants app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Restaurant, RestaurantSettings
from .serializers import (
    RestaurantListSerializer, RestaurantDetailSerializer,
    RestaurantCreateUpdateSerializer, RestaurantSettingsSerializer
)


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for restaurants.
    """
    queryset = Restaurant.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        elif self.action == 'list':
            return RestaurantListSerializer
        else:
            return RestaurantCreateUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Restaurant.objects.all()
        return Restaurant.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        restaurant = self.get_object()
        if self.request.user != restaurant.owner and not self.request.user.is_staff:
            self.permission_denied(self.request)
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user != instance.owner and not self.request.user.is_staff:
            self.permission_denied(self.request)
        instance.delete()
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def restaurant_settings(self, request, slug=None):
        """Get or update restaurant settings"""
        restaurant = self.get_object()
        if request.method == 'GET':
            rest_settings, created = RestaurantSettings.objects.get_or_create(restaurant=restaurant)
            serializer = RestaurantSettingsSerializer(rest_settings)
            return Response(serializer.data)
        else:
            rest_settings, created = RestaurantSettings.objects.get_or_create(restaurant=restaurant)
            serializer = RestaurantSettingsSerializer(
                rest_settings,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def menu_categories(self, request, slug=None):
        """Get restaurant menu categories"""
        restaurant = self.get_object()
        categories = restaurant.menu_categories.filter(is_active=True)
        
        from apps.menu.serializers import MenuCategorySerializer
        serializer = MenuCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tables(self, request, slug=None):
        """Get restaurant tables"""
        restaurant = self.get_object()
        tables = restaurant.tables.filter(is_active=True)
        
        from apps.tables.serializers import TableListSerializer
        serializer = TableListSerializer(tables, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_restaurants(self, request):
        """Get current user's restaurants"""
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется аутентификация'}, status=status.HTTP_401_UNAUTHORIZED)
        
        restaurants = Restaurant.objects.filter(owner=request.user)
        serializer = RestaurantListSerializer(restaurants, many=True)
        return Response(serializer.data)
