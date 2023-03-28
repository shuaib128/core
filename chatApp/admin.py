from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatImage

# Register your models here.
admin.site.register(ChatRoom)
admin.site.register(ChatImage)
admin.site.register(ChatMessage)