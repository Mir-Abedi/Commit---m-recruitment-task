from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=50)
    phone_num = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    balance = models.IntegerField(default=0)

    class Meta:
        db_table = "USERSTABLE"
