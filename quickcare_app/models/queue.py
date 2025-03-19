from django.db import models
from django.utils.timezone import now
from .doc_patient import Doctor, Patient
from .hospital_staff import Room
from .misc import Notification


class Queue(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("waiting", "Waiting"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled")
        ],
        default="waiting"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.position}"

    @staticmethod
    def reset_daily_queue():
        """🔥 Har kuni kechasi navbatni yangilash"""
        Queue.objects.all().delete()

    @staticmethod
    def add_patient_to_queue(patient, doctor):
        """➕ Bemorga avtomatik navbat raqami berish"""
        today = now().date()
        start_time = now().replace(hour=8, minute=0, second=0)
        end_time = now().replace(hour=20, minute=0, second=0)

        if start_time <= now() <= end_time:
            last_position = Queue.objects.filter(created_at__date=today).count() + 1
            queue = Queue.objects.create(
                patient=patient,
                doctor=doctor,
                position=last_position
            )

            Notification.send_notification(
                recipient=patient,
                message=f"📢 Hurmatli {patient.user.username}, sizning navbatingiz {last_position}.",
                notification_type="queue_update"
            )
            return queue
        return None

    def cancel_queue(self):
        """❌ Bemor navbatdan voz kechsa, keyingi bemorlarning navbati oldinga siljiydi"""
        if self.status == "waiting":
            self.status = "cancelled"
            self.save()

            # Keyingi bemorlarning navbatini oldinga siljitish
            next_patients = Queue.objects.filter(position__gt=self.position, status="waiting").order_by("position")
            for q in next_patients:
                q.position -= 1
                q.save()

            Notification.send_notification(
                recipient=self.patient,
                message=f"❌ Sizning navbatingiz bekor qilindi.",
                notification_type="queue_update"
            )

            if next_patients.exists():
                next_patient = next_patients.first()
                Notification.send_notification(
                    recipient=next_patient.patient,
                    message=f"📢 Hurmatli {next_patient.patient.user.username}, navbatingiz bir pog‘ona oldinga siljidi.",
                    notification_type="queue_update"
                )
