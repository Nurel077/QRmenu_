"""
URL configuration for restaurant_qr_project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/restaurants/', include('apps.restaurants.urls')),
    path('api/tables/', include('apps.tables.urls')),
    path('api/menu/', include('apps.menu.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    
    # Main application views
    path('', include('apps.restaurants.urls_web')),  # Landing page
    path('table/', include('apps.tables.urls_web')),  # Guest interface
    path('menu/', include('apps.restaurants.urls_web')),  # Menu pages
    path('waiter/', include('apps.accounts.urls_waiter')),  # Waiter panel
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Custom admin site configuration
admin.site.site_header = "RestaurantQR Администрирование"
admin.site.site_title = "RestaurantQR Admin"
admin.site.index_title = "Панель управления"
