from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        conversation = instance.conversation
        sender = instance.sender

        # Crear notificaciones para todos los participantes excepto el remitente
        for participant in conversation.participants.exclude(id=sender.id):
            Notification.objects.create(
                user=participant,
                message=f"Tienes un nuevo mensaje de {sender.username}",
                type=Notification.MESSAGE,
            )
