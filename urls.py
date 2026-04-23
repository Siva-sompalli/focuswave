# focuswave_backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Map all API endpoints to /api/
    path('api/', include('focuswave_api.urls')), 
]