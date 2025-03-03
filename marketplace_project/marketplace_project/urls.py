"""
URL configuration for marketplace_project project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
]
