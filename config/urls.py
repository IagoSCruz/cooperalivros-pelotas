"""
URL configuration for Library Management System.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from books.views import BookViewSet
from loans.views import LoanViewSet
from users.views import LibraryUserViewSet

# API Router
router = routers.DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'users', LibraryUserViewSet, basename='libraryuser')
router.register(r'loans', LoanViewSet, basename='loan')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    # API
    path('api/', include(router.urls)),
    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'
    ),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Frontend
    path('', include('frontend.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
