from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    two_factor_secret = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.username