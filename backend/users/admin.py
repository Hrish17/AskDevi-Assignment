from django.contrib import admin
from .models import UserSession, UserBirthDetails, ChatMessage

admin.site.register(UserSession)
admin.site.register(UserBirthDetails)
admin.site.register(ChatMessage)
