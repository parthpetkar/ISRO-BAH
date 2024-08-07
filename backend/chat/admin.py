from django.contrib import admin
from .models import Chat

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('user_input', 'generated_responses')
    readonly_fields = ('created_at',)
