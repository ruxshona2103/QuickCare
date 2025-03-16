#doctor, patients, appointment, notification, patientmedicine
from math import trunc

from django.db import models
from django.contrib.auth import get_user_model
from .hospital_staff import Department, Room

User = get_user_model()

class Doctor(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="shifokor")
    specialization = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "shifokor"
        verbose_name_plural = "shifokorlar"

    def __str__(self):
        return f"{self.full_name} ({self.specialization}) - Room: {self.room.room_number if self.room else 'N/A'}"


from django.db import models

class Patient(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ism sharifi")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="telefon raqami")
    birth_date = models.DateField()  # Tug‘ilgan sana
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female")], verbose_name="jinsi")
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)

    # 🏥 Tibbiy ma’lumotlar
    medical_history = models.TextField(blank=True, null=True)  # Kasallik tarixi
    blood_type = models.CharField(max_length=5, choices=[("A+", "A+"), ("A-", "A-"),
                                                          ("B+", "B+"), ("B-", "B-"),
                                                          ("AB+", "AB+"), ("AB-", "AB-"),
                                                          ("O+", "O+"), ("O-", "O-")],
                                  blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_diseases = models.TextField(blank=True, null=True)
    complaints = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "bemor"
        verbose_name_plural = "bemorlar"

    def __str__(self):
        return f"Bemor {self.username}, telefon raqami {self.phone_number}"








