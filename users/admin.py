from django.contrib import admin
from .models import Profile, FCMToken

# Register your models here.
admin.site.register(Profile)
admin.site.register(FCMToken)