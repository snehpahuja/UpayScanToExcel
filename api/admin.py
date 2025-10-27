from django.contrib import admin
from .models import Profile, Place, Review, Badge, UserBadge

admin.site.register(Profile)
admin.site.register(Place)
admin.site.register(Review)
admin.site.register(Badge)
admin.site.register(UserBadge)
