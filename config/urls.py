"""
Root URL configuration for EMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ems.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site headers
admin.site.site_header = "EMS Administration"
admin.site.site_title = "Event Management System"
admin.site.index_title = "Dashboard"
