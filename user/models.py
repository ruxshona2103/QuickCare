from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('patient', 'Patient'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)


    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
