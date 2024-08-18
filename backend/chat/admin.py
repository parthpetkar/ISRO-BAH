from django.contrib import admin
from .models import Chat

class ChatAdmin(admin.ModelAdmin):
    """
    Admin class for the Chat model.

    This class is used to define the behavior of the Chat model in the Django admin interface.

    Attributes:
        list_display (list): A list of fields to be displayed in the admin interface's list view.
        search_fields (list): A list of fields to be searchable in the admin interface.
        readonly_fields (list): A list of fields that are read-only in the admin interface.

    Args:
        model (Chat): The model to be administered.

    Returns:
        None: This method does not return any value.
    """

    list_display = ('id', 'created_at')
    search_fields = ('user_input', 'generated_responses')
    readonly_fields = ('created_at',)