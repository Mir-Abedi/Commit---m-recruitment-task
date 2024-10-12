from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_num = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "TABLE1"

    def __str__(self):
        return f'{self.name} A.K.A {self.username}'