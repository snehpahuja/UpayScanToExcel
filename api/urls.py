from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    PlaceViewSet,
    ReviewViewSet,
    BadgeViewSet,
    UserBadgeViewSet,
    PlaceListCreateView,  # existing
    SignupView,
    LoginView
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'places', PlaceViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'badges', BadgeViewSet)
router.register(r'userbadges', UserBadgeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('places-list/', PlaceListCreateView.as_view(), name='place-list-create'),
    # ------------------ New signup/login endpoints ------------------
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]
