from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True, default=get_random_string(20))
    gender = models.CharField(max_length=15, blank=True)