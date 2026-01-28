"""
Views and ViewSets for accounts app.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    GuestSessionSerializer, ChangePasswordSerializer
)
from .models import GuestSession

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for user operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def list(self, request):
        """List all users (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get user details"""
        try:
            user = User.objects.get(pk=pk)
            if user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': 'Неправильный пароль'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response({'detail': 'Пароль изменен успешно'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """
    Register new user.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {'detail': 'Пользователь успешно зарегистрирован', 'data': response.data},
            status=status.HTTP_201_CREATED
        )


class GuestSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for guest sessions.
    """
    queryset = GuestSession.objects.all()
    serializer_class = GuestSessionSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create new guest session"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)