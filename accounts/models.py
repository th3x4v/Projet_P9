from django.db import models
from django.contrib.auth.models import AbstractUser

# https://docs.djangoproject.com/fr/4.0/topics/auth/customizing/
#using-a-custom-user-model-when-starting-a-project


class User(AbstractUser):
    """Represent a Custom user"""
    pass
