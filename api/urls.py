from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    PlaceViewSet,
    ReviewViewSet,
    BadgeViewSet,
    UserBadgeViewSet,
    SignupView,
    LoginView
)

# -----------------------------
# Router for all ViewSets
# -----------------------------
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'places', PlaceViewSet)       # <-- this handles listing/creating places
router.register(r'reviews', ReviewViewSet)
router.register(r'badges', BadgeViewSet)
router.register(r'userbadges', UserBadgeViewSet)

# -----------------------------
# URL patterns
# -----------------------------
urlpatterns = [
    path('', include(router.urls)),             # all viewset routes
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]

