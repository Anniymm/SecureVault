from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TwoFactorSettings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_2fa_settings(sender, instance, created, **kwargs):
    if created:
        TwoFactorSettings.objects.create(user=instance)
