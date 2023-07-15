from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255)
    birthday = models.DateField()
    username = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Added phone_number field    
    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')

    def get_next_username(self):
        latest_user = CustomUser.objects.order_by('-id').first()
        if latest_user:
            latest_username = latest_user.username
            prefix = latest_username[:2]
            suffix = int(latest_username[3:])
            next_username = f"{prefix}-{suffix + 1:04d}"
            while CustomUser.objects.filter(username=next_username).exists():  # Check if the username already exists
                suffix += 1
                next_username = f"{prefix}-{suffix:04d}"
            return next_username
        return "DF-0001"

    def save(self, *args, **kwargs):
        if not self.username:
            if self.pk:  # Check if the user already exists
                existing_user = CustomUser.objects.get(pk=self.pk)
                if existing_user.username == self.username:  # Username hasn't changed
                    super().save(*args, **kwargs)
                    return
            self.username = self.get_next_username()
        super().save(*args, **kwargs)

from django.db import models
from authentication.models import CustomUser

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field='username')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    # Add more fields as needed
