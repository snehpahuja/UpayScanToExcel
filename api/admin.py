from django.contrib import admin
from .models import Profile, Place, Review, Badge, UserBadge


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'points', 'location', 'created_at', 'is_deleted')
    search_fields = ('username', 'location')
    list_filter = ('role', 'is_deleted')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'neighborhood', 'price_level', 'rating', 'veg_only', 'created_at')
    search_fields = ('name', 'neighborhood', 'categories')
    list_filter = ('veg_only', 'price_level')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'rating', 'created_at')
    search_fields = ('user__username', 'place__name')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required', 'created_at')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at', 'active')
