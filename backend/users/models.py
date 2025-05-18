from django.db import models
import uuid


class UserSession(models.Model):
    """
    A lightweight representation of a user session, tracked via UUID.
    """
    session_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.session_id)


class UserBirthDetails(models.Model):
    """
    Stores birth details for a user session. 
    The tuple (name, date_of_birth, time_of_birth, place_of_birth) must be unique.
    """
    session = models.OneToOneField(
        UserSession, on_delete=models.CASCADE, related_name='birth_details')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    time_of_birth = models.TimeField()
    place_of_birth = models.CharField(max_length=100)
    rashi_report = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.session.session_id})"


class ChatMessage(models.Model):
    """
    Stores individual chat messages for a session.
    """
    session = models.ForeignKey(
        UserSession, on_delete=models.CASCADE, related_name='messages')
    user_message = models.TextField()
    devi_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # newest first

    def __str__(self):
        return f"Chat @ {self.timestamp} - Session {self.session.session_id}"
