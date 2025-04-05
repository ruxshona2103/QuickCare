from django.db import models
from .doc_patient import  Doctor, Patient



class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("queue_update", "Queue Update"),
        ("appointment_reminder", "Appointment Reminder"),
        ("general", "General Message"),
        ("emergency_alert", "Emergency Alert"),
    )

    recipient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Qabul qiluvchi")
    message = models.TextField(verbose_name="Xabar matni")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")
    is_read = models.BooleanField(default=False, verbose_name="O'qilganmi?")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="queue_update")
    via_sms = models.BooleanField(default=True, verbose_name="SMS orqali")
    via_telegram = models.BooleanField(default=True, verbose_name="Telegram orqali")
    via_email = models.BooleanField(default=False, verbose_name="Email orqali")

    class Meta:
        verbose_name = "bildirishnoma"
        verbose_name_plural = "bildirishnomalar"

    def __str__(self):
        return f"📢 {self.recipient.full_name} ga xabar yuborildi ({self.notification_type})"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @staticmethod
    def send_notification(recipient, message, notification_type="queue_update", via_sms=True, via_telegram=True, via_email=False):
        notification = Notification.objects.create(
            recipient=recipient,
            message=message,
            notification_type=notification_type,
            via_sms=via_sms,
            via_telegram=via_telegram,
            via_email=via_email
        )
        return notification




class Comment(models.Model):
    author = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "izoh"
        verbose_name_plural = "izohlar"

    def __str__(self):
        return f"{self.author.username} -> {self.doctor.user.username}: {self.text[:30]}"


class Review(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey("Room", on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "fikr"
        verbose_name_plural = "fikrlar"

    def __str__(self):
        return f"Review by {self.patient.user.username} - {self.rating}⭐️"

    class Meta:
        ordering = ["-created_at"]

class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.doctor.user.username} to Review {self.review.id}"

    class Meta:
        verbose_name = "fikr qaytarish"
        verbose_name_plural = "fikr qaytarishlar"




