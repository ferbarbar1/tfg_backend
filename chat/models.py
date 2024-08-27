from django.db import models
from authentication.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Conversation between {', '.join(user.username for user in self.participants.all())}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        CustomUser, related_name="messages", on_delete=models.CASCADE
    )
    content = models.TextField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.conversation.last_message = self.timestamp
        self.conversation.save()


class Notification(models.Model):
    MESSAGE = "message"
    REMINDER = "reminder"
    NOTIFICATION_TYPES = [
        (MESSAGE, "Message"),
        (REMINDER, "Reminder"),
    ]

    user = models.ForeignKey(
        CustomUser, related_name="notifications", on_delete=models.CASCADE
    )
    message = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default=MESSAGE)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.created_at}"


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        conversation = instance.conversation
        sender = instance.sender

        for participant in conversation.participants.exclude(id=sender.id):
            Notification.objects.create(
                user=participant,
                message=f"Tienes un nuevo mensaje de {sender.username}",
            )
