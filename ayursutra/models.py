from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

USER_ROLES = {
    "Practitioner": "Practitioner",
    "Patient": "Patient"
}

PRIORITIES ={
    "High": "High",
    "Medium": "Medium",
    "Low": "Low"
}

class User(AbstractUser):

    username = models.CharField(max_length=256, unique=False, null=True, blank=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Patient(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dateOfBirth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.firstName

class Practitioner(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="practitioners/")
    hospitalName = models.CharField(max_length=100)
    experience = models.CharField(max_length=10)
    image_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.firstName

class NotificationTypes(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.firstName

class UserNotifications(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    priority = models.CharField(max_length=7, choices=PRIORITIES)
    datetime = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.firstName