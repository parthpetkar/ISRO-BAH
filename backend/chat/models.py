from django.db import models

class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    input_response_pairs = models.JSONField()  # Store user inputs and responses as a JSON object
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"

    def add_message(self, message_id, text, is_bot):
        # Assuming input_response_pairs is a list of messages
        messages = self.input_response_pairs or []
        messages.append({"id": message_id, "text": text, "isBot": is_bot})
        self.input_response_pairs = messages
        self.save()
