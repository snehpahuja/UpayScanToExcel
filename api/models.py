from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Base model for audit + soft delete
class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_updated"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------
class Profile(AbstractUser, BaseModel):
    role = models.CharField(max_length=10, default='user')
    points = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Recommendation attributes
    segment = models.CharField(max_length=100, blank=True, null=True)
    home_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    preferred_categories = models.JSONField(blank=True, null=True)
    price_preference = models.PositiveSmallIntegerField(blank=True, null=True)
    distance_tolerance_km = models.FloatField(blank=True, null=True)
    ambience_preferences = models.JSONField(blank=True, null=True)
    explore_rate = models.FloatField(blank=True, null=True)
    age_group = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


# ---------------------------------------------------------------------
# Place Model
# ---------------------------------------------------------------------
class Place(BaseModel):
    place_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    cluster_label = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    categories = models.CharField(max_length=200, blank=True, null=True)
    price_level = models.PositiveSmallIntegerField(blank=True, null=True)
    rating = models.FloatField(default=0)
    user_rating_count = models.PositiveIntegerField(default=0)
    ambience = models.CharField(max_length=100, blank=True, null=True)
    veg_only = models.BooleanField(default=False)
    cat_list = models.JSONField(blank=True, null=True)
    reviews_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------
# Review Model
# ---------------------------------------------------------------------
class Review(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    dwell_time_sec = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "place")

    def __str__(self):
        return f"{self.user.username} → {self.place.name}"


# ---------------------------------------------------------------------
# Interaction Model
# ---------------------------------------------------------------------
class Interaction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    rating = models.FloatField(blank=True, null=True)
    dwell_time_sec = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.type} {self.place.name}"


# ---------------------------------------------------------------------
# Badges & Gamification
# ---------------------------------------------------------------------
class Badge(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField(default=0)
    icon_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class UserBadge(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.username} - {self.badge.title}"


