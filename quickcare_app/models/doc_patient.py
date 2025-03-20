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


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="foydalanuvchi")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="telefon raqami")
    birth_date = models.DateField(verbose_name="tug'ilgan sanasi")  # Tug‘ilgan sana
    address = models.TextField(blank=True, null=True, verbose_name="manzili")
    emergency_contact = models.CharField(max_length=15, blank=True, null=True, verbose_name="favqulotda qo'ng'iroq")
    medical_history = models.TextField(blank=True, null=True, verbose_name="kasallik tarixi")
    allergies = models.TextField(blank=True, null=True, verbose_name="allergiya")
    chronic_diseases = models.TextField(blank=True, null=True, verbose_name="surunkali kasalliklar")
    complaints = models.TextField(blank=True, null=True, verbose_name="shikoyatlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="yaratilgan sanasi")

    class Meta:
        verbose_name = "bemor"
        verbose_name_plural = "bemorlar"

    def __str__(self):
        return f"Bemor {self.username}, telefon raqami {self.phone_number}"








