from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

USER_ROLES = {
    "Doctor": "Doctor",
    "Patient": "Patient"
}

PRIORITIES ={
    "High": "High",
    "Medium": "Medium",
    "Low": "Low"
}

def get_file_location(instance):

    if instance.role == "Doctor":
        return "doctors/"
    
    return "patients/"

class User(AbstractUser):

    username = models.CharField(max_length=256, unique=False, null=True, blank=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to=get_file_location, null=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

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
    _type = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.user.firstName
    
class DoctorProgram(models.Model):

    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="programs")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    total_phases = models.PositiveIntegerField(null=True)
    total_sessions = models.PositiveIntegerField(null=True)

    def __str__(self):

        return f"{self.doctor.firstName} {self.doctor.lastName}: {self.title}"

class ProgramPhase(models.Model):

    program = models.ForeignKey(DoctorProgram, on_delete=models.CASCADE, related_name="phases")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    total_sessions = models.PositiveIntegerField(null=True)

    def __str__(self):

        return self.program.title