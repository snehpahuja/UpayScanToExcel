from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Place, Review, Badge, UserBadge
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        fields = [
            'created_by', 'created_at',
            'updated_by', 'updated_at',
            'deleted_by', 'deleted_at',
            'is_deleted'
        ]


class ProfileSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'points', 'location', 'bio',
            'segment', 'home_neighborhood',
            'preferred_categories', 'price_preference',
            'distance_tolerance_km', 'ambience_preferences',
            'explore_rate', 'age_group'
        ]


# -------------------- Signup Serializer --------------------
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Create a profile if needed; here your ProfileSerializer is based on User, so no extra step
        return user


class PlaceSerializer(BaseModelSerializer):
    class Meta:
        model = Place
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'place_id', 'name', 'neighborhood',
            'cluster_label', 'latitude', 'longitude',
            'categories', 'price_level', 'rating',
            'user_rating_count', 'ambience', 'veg_only',
            'cat_list', 'reviews_text'
        ]


class ReviewSerializer(BaseModelSerializer):
    class Meta:
        model = Review
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'user', 'place', 'rating', 'comment', 'summary'
        ]
        read_only_fields = ['user']

class BadgeSerializer(BaseModelSerializer):
    class Meta:
        model = Badge
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'title', 'description', 'points_required', 'icon_url'
        ]


class UserBadgeSerializer(BaseModelSerializer):
    class Meta:
        model = UserBadge
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'user', 'badge', 'awarded_at', 'active'
        ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "user_id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        })
        return data