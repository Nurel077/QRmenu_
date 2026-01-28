"""
URL configuration for tables app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.TableViewSet, basename='table')
router.register(r'sessions', views.TableSessionViewSet, basename='table-session')

urlpatterns = [
    path('', include(router.urls)),
]
