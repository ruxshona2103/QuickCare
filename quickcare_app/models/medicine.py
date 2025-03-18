#appointment, notification, patientmedicine
from django.db import models
from . import Patient

class Medicine(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Dori nomi
    description = models.TextField(blank=True, null=True)  # Dori haqida qisqacha ma’lumot
    usage = models.CharField(
        max_length=20,
        choices=[
            ("painkiller", "Painkiller"),
            ("antibiotic", "Antibiotic"),
            ("anti-inflammatory", "Anti-inflammatory"),
            ("other", "Other")
        ],
        default="other"
    )  # Dorining turi
    side_effects = models.TextField(blank=True, null=True)  # Yon ta’sirlari
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Narxi
    is_available = models.BooleanField(default=True)  # Mavjud yoki yo‘qligi

    def __str__(self):
        return self.name


class Pharmacy(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.medicine.name} - {self.stock} left"


class PatientMedicine(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)
    prescribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.medicine.name} ({self.dosage})"

