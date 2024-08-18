from django.db import models

class Chat(models.Model):
    """
    A model representing a chat conversation.

    Attributes:
    id (AutoField): A unique identifier for the chat conversation.
    input_response_pairs (JSONField): A JSON object to store user inputs and responses.
    created_at (DateTimeField): The date and time when the chat conversation was created.

    Methods:
    __str__(self): Returns a string representation of the Chat object.
    add_message(self, message_id, text, is_bot): Adds a new message to the chat conversation.

    """

    id = models.AutoField(primary_key=True)
    input_response_pairs = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the Chat object.

        This method returns a string containing the Chat's id and creation date.

        Args:
        self (Chat): An instance of the Chat model.

        Returns:
        str: A string representation of the Chat object in the format "Chat {id} - {created_at}".
        """
        return f"Chat {self.id} - {self.created_at}"

    def add_message(self, message_id, text, is_bot):
        """
        Adds a new message to the chat conversation.

        Args:
        self (Chat): An instance of the Chat model.
        message_id (int): A unique identifier for the new message.
        text (str): The text content of the new message.
        is_bot (bool): A boolean value indicating whether the new message is from a bot.

        Returns:
        None
        """
        # Assuming input_response_pairs is a list of messages
        messages = self.input_response_pairs or []
        messages.append({"id": message_id, "text": text, "isBot": is_bot})
        self.input_response_pairs = messages
        self.save()