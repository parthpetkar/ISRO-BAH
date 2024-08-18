from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.

    This serializer is used to convert the Chat model's data into a format that can be easily consumed by the API.

    Args:
    - model (Chat): The model to be serialized.
    - fields (str): All fields of the model to be included in the serialization.

    Returns:
    - serializer (ChatSerializer): An instance of the ChatSerializer class.
    """

    class Meta:
        model = Chat
        fields = '__all__'