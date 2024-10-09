from django.db import models
from authentication.models import CustomUser
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver


class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Conversation between {', '.join(user.username for user in self.participants.all())}"

    def clean(self):
        if self.participants.count() < 2:
            raise ValidationError("A conversation must have at least two participants.")
        if self.last_message and self.last_message < self.created_at:
            raise ValidationError(
                "Last message timestamp cannot be earlier than the creation timestamp."
            )


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
        if not self.content.strip():
            raise ValidationError("Message content cannot be empty.")
        if self.sender not in self.conversation.participants.all():
            raise ValidationError("Sender must be a participant in the conversation.")
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

    def clean(self):
        if not self.message.strip():
            raise ValidationError("Notification message cannot be empty.")
        if self.type not in dict(self.NOTIFICATION_TYPES).keys():
            raise ValidationError("Invalid notification type.")


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
