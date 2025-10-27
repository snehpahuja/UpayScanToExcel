from rest_framework import viewsets, generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Profile, Place, Review, Badge, UserBadge
from .serializers import (
    ProfileSerializer,
    PlaceSerializer,
    ReviewSerializer,
    BadgeSerializer,
    UserBadgeSerializer
)


# ---------- PROFILE ----------
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# ---------- PLACES ----------
class PlaceListCreateView(generics.ListCreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# ---------- REVIEWS ----------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# ---------- BADGES ----------
class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# ---------- USER BADGES ----------
class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all()
    serializer_class = UserBadgeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

