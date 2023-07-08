from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255)
    birthday = models.DateField()
    username = models.CharField(max_length=255, unique=True)

    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')

    def save(self, *args, **kwargs):
        if not self.username:
            birth_year = str(self.birthday.year)
            self.username = self.name + birth_year
        super().save(*args, **kwargs)

from django.db import models
from authentication.models import CustomUser

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field='username')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    # Add more fields as needed
