"""
Web URLs for restaurants app (Landing page, guest interface).
"""
from django.urls import path
from django.views.generic import TemplateView

app_name = 'restaurants_web'

urlpatterns = [
    # Landing page
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    # Guest menu
    path('menu/', TemplateView.as_view(template_name='guest_menu.html'), name='guest_menu'),
]
