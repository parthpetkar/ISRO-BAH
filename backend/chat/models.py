from django.db import models

class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    input_response_pairs = models.JSONField()  # Store user inputs and responses as a JSON object
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"
