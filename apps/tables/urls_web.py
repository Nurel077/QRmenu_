"""
Web URLs for tables app (Guest interface).
"""
from django.urls import path
from django.views.generic import TemplateView

app_name = 'tables_web'

urlpatterns = [
    # Guest interface
    path('<slug:restaurant_slug>/<str:table_number>/', TemplateView.as_view(template_name='guest_menu.html'), name='guest_menu'),
]
