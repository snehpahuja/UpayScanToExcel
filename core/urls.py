"""
URL configuration for UPAY Document Processing project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


def home(request):
    """Simple home view to verify backend is running"""
    return HttpResponse("""
    <html>
        <head><title>UPAY API</title></head>
        <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
            <h1>UPAY Document Processing System</h1>
            <p>Backend is running successfully!</p>
            <div style="margin-top: 30px;">
                <a href="/swagger/" style="margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">API Documentation (Swagger)</a>
                <a href="/redoc/" style="margin: 10px; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">API Documentation (ReDoc)</a>
                <a href="/admin/" style="margin: 10px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;">Admin Panel</a>
            </div>
        </body>
    </html>
    """)


# =====================================================
# Swagger/OpenAPI Schema Configuration
# =====================================================
schema_view = get_schema_view(
    openapi.Info(
        title="UPAY Document Processing API",
        default_version="v1",
        description="""
# UPAY Document Processing System API Documentation

## Overview
API for managing document uploads, OCR processing, review workflows, and analytics dashboards.

## Key Features
- **Document Management**: Upload, categorize, and process scanned documents (PDF, JPG, PNG)
- **OCR Processing**: Automated text extraction with confidence scoring
- **Review Workflow**: Manual verification and correction of extracted data
- **Analytics**: Comprehensive dashboards for attendance, grades, enrollment, finances, and more
- **User Management**: Role-based access control (Employee/Admin)
- **Store Management**: Track requisitions and receivements
- **Visitor Tracking**: Monitor visitor logs across centers

## Authentication
This API uses JWT (JSON Web Token) authentication:
1. Login at `/api/login/` to get access and refresh tokens
2. Include token in header: `Authorization: Bearer <access_token>`
3. Refresh tokens at `/api/token/refresh/` when expired

## User Roles
- **Employee**: Upload and manage own documents, view assigned center data
- **Admin**: Full system access including user management and all centers

## Email Requirement
All users must have `@upayngo.com` email addresses.
        """,
        terms_of_service="https://www.upayngo.com/terms/",
        contact=openapi.Contact(email="support@upayngo.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# =====================================================
# URL Patterns
# =====================================================
urlpatterns = [
    # Home
    path("", home, name="home"),
    
    # Admin Interface
    path("admin/", admin.site.urls),
    
    # API Routes
    path("api/", include("api.urls")),
    
    # JWT Token Endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # API Documentation
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^swagger\.json$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]


# =====================================================
# Serve Media and Static Files in Development
# =====================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# =====================================================
# Custom Admin Site Configuration
# =====================================================
admin.site.site_header = "UPAY Document Processing System"
admin.site.site_title = "UPAY Admin"
admin.site.index_title = "Welcome to UPAY Administration"