from django.db import models
from .doc_patient import Patient, Doctor
from .misc import Notification

class Emergency(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved")
        ],
        default="pending"
    )
    ambulance_requested = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"🚨 {self.patient.username} - {self.get_status_display()}"


    def request_ambulance(self):
        self.ambulance_requested = True
        self.status = "in_progress"
        self.save()

        Notification.send_notification(
            recipient=self.patient,
            message="🚑 Tez yordam sizning manzilingizga yo‘l oldi!",
            notification_type="emergency"
        )


class Ambulance(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)  # Mashina raqami
    status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("on_duty", "On Duty"),  # Ishlayapti
            ("unavailable", "Unavailable")  # Ishlamayapti
        ],
        default="available"
    )
    current_location = models.CharField(max_length=255, blank=True, null=True)  # Hozir qayerda?

    def __str__(self):
        return f"🚑 {self.plate_number} - {self.get_status_display()}"


