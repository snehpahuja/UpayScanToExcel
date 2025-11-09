from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSignupSerializer
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from .models import Place, Review, Badge, UserBadge
from .serializers import (
    ProfileSerializer, PlaceSerializer, ReviewSerializer,
    BadgeSerializer, UserBadgeSerializer
)

User = get_user_model()


# ------------------------------
# Base ViewSet (shared config)
# ------------------------------
class BaseViewSet(viewsets.ModelViewSet):
    """Applies global authentication and permission logic."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# ------------------------------
# Profile / User
# ------------------------------
class ProfileViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        # Non-admins can only view their own profile
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)


# ------------------------------
# Places
# ------------------------------
class PlaceViewSet(BaseViewSet):
    queryset = Place.objects.filter(is_deleted=False)
    serializer_class = PlaceSerializer


# ------------------------------
# Reviews
# ------------------------------
class ReviewViewSet(BaseViewSet):
    queryset = Review.objects.select_related('user', 'place')
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ------------------------------
# Badges
# ------------------------------
class BadgeViewSet(BaseViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins manage badges


# ------------------------------
# User Badges
# ------------------------------
class UserBadgeViewSet(BaseViewSet):
    queryset = UserBadge.objects.select_related('user', 'badge')
    serializer_class = UserBadgeSerializer

# ------------------------------
# User Signup
# ------------------------------
class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]  # anyone can sign up

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })


# ------------------------------
# User Login (JWT)
# ------------------------------
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
