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
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)  # Telefon raqami
    address = models.TextField(blank=True, null=True)  # Manzil
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profil rasmi
    date_of_birth = models.DateField(blank=True, null=True)  # Tug‘ilgan sana
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female')), blank=True, null=True)  # Jinsi
    is_active = models.BooleanField(default=True)  # Foydalanuvchi aktiv yoki yo‘qligi
    date_joined = models.DateTimeField(auto_now_add=True)  # Ro‘yxatdan o‘tgan sana

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
