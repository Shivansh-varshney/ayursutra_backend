from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

USER_ROLES = {
    "Doctor": "Doctor",
    "Patient": "Patient"
}

PRIORITIES = {
    "High": "High",
    "Medium": "Medium",
    "Low": "Low"
}

STATUS_CHOICES = {
    'Upcoming':'Upcoming',
    'Scheduled':'Scheduled',
    'Rescheduled':'Rescheduled',
    'Completed': 'Completed',
    'Cancelled': 'Cancelled',
}

PLATFORM_CHOICES = {
    "android": "Android",
    "ios": "iOS",
    "windows": "Windows",
    "linux": "Linux",
    "web": "Web Browser",
}

def get_file_location(instance):

    if instance.role == "Doctor":
        return "doctors/"
    
    return "patients/"

class Clinic(models.Model):

    name = models.CharField(max_length=200)
    location = models.TextField()
    contact = models.CharField(max_length=15)

class User(AbstractUser):

    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors", limit_choices_to={'role': 'doctor'})
    username = models.CharField(max_length=256, unique=False, null=True, blank=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to=get_file_location, null=True)
    is_verified = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class PatientProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allergies = models.TextField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    dateOfBirth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.firstName

class NotificationType(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.title

class UserNotificationPreference(models.Model):

    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name="user_preferences")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="programs", null=True)
    doctor = models.ManyToManyField(User, related_name="programs", limit_choices_to={'role': 'doctor'})
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    total_phases = models.PositiveIntegerField(null=True)
    total_sessions = models.PositiveIntegerField(null=True)
    duration_per_session = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):

        return f"{self.clinic.name}: {self.title}"

class ProgramPhase(models.Model):

    program = models.ForeignKey(DoctorProgram, on_delete=models.CASCADE, related_name="phases")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=256)
    total_sessions = models.PositiveIntegerField(null=True)

    def __str__(self):

        return self.program.title

class PatientTreatment(models.Model):

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, null=True, related_name="treatments")
    program = models.ForeignKey(DoctorProgram, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient.user.firstName} {self.patient.user.lastName} - {self.program.title}" if self.patient else 'Unknown'
    
class PatientPhase(models.Model):

    treatment = models.ForeignKey(PatientTreatment, on_delete=models.CASCADE, related_name="phases")
    phase = models.ForeignKey(ProgramPhase, on_delete=models.SET_NULL, null=True)
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.treatment.patient.user.firstName} {self.treatment.patient.user.lastName}" if self.treatment else 'Unknown'

class Session(models.Model):

    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sessions_conducted", limit_choices_to={'role': 'doctor'})
    phase = models.ForeignKey(PatientPhase, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    # location = models.CharField(max_length=200, null=True)
    duration = models.PositiveIntegerField(default=0)
    patient_approval = models.BooleanField(default=False)
    doctor_approval = models.BooleanField(default=False)
    doctor_notes = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.phase.treatment.patient.user.firstName} {self.phase.treatment.patient.user.lastName}" if self.phase else 'Unknown'

class Vitals(models.Model):

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="vitals")
    energy = models.PositiveIntegerField(default=0)
    sleep = models.PositiveIntegerField(default=0)
    stress = models.PositiveIntegerField(default=0)
    digestion = models.PositiveIntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.firstName} {self.patient.user.lastName}"
    
class FeedBack(models.Model):

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="feedbacks")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.IntegerField(default=3)
    review = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient.user.firstName if self.patient else 'Unknown'

# push notifications
class Device(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    device_token = models.CharField(max_length=512, unique=True)
    device_id = models.CharField(max_length=256, null=True, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.platform}"

class NotificationDelivery(models.Model):
    notification = models.ForeignKey(UserNotifications, on_delete=models.CASCADE, related_name="deliveries")
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("pending","Pending"),("sent","Sent"),("failed","Failed")])
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Delivery to {self.device.platform} ({self.status})"
