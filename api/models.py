from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# ------------------------
# Base Audit Model
# ------------------------
class AuditModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="%(class)s_created", 
        on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="%(class)s_updated", 
        on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="%(class)s_deleted", 
        on_delete=models.SET_NULL, null=True, blank=True
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ------------------------
# Custom User Model
# ------------------------
class Profile(AbstractUser, AuditModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    points = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Recommendation-related
    segment = models.CharField(max_length=100, blank=True, null=True)
    home_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    preferred_categories = models.JSONField(blank=True, null=True)
    price_preference = models.IntegerField(blank=True, null=True)
    distance_tolerance_km = models.FloatField(blank=True, null=True)
    ambience_prefs = models.JSONField(blank=True, null=True)
    explore_rate = models.FloatField(default=0)
    age_group = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username


# ------------------------
# Place Model
# ------------------------
class Place(AuditModel):
    place_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    cluster_label = models.IntegerField(blank=True, null=True)
    lat = models.FloatField()
    lng = models.FloatField()
    categories = models.JSONField(blank=True, null=True)
    price_level = models.IntegerField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    user_rating_count = models.IntegerField(blank=True, null=True)
    ambience = models.CharField(max_length=100, blank=True, null=True)
    veg_only = models.BooleanField(default=False)
    cat_list = models.JSONField(blank=True, null=True)
    reviews = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------------
# Review Model
# ------------------------
class Review(AuditModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    summary = models.TextField(blank=True)  # summarised text (from chatbot)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.place.name}"


# ------------------------
# Badge System
# ------------------------
class Badge(AuditModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.IntegerField(default=0)
    icon = models.URLField(blank=True)

    def __str__(self):
        return self.title


class UserBadge(AuditModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.title}"


# ------------------------
# Interaction (for recommendation tracking)
# ------------------------
class Interaction(AuditModel):
    interaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)  # "click", "visit", "rating"
    rating = models.FloatField(blank=True, null=True)
    dwell_sec = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.place.name}"

