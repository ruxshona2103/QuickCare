from django.db import models
from django.utils.translation import gettext_lazy as _

from .doc_patient import Patient, Doctor
from .misc import Notification


class Emergency(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Kutilmoqda')
        IN_PROGRESS = 'in_progress', _('Jarayonda')
        RESOLVED = 'resolved', _('Hal qilindi')

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name=_("Bemor"))
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Shifokor")
    )
    description = models.TextField(verbose_name=_("Tavsif"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Holat")
    )
    ambulance_requested = models.BooleanField(default=True, verbose_name=_("Tez yordam"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    def __str__(self):
        return f"🚨 {self.patient.full_name} - {self.get_status_display()}"

    def request_ambulance(self, ambulance=None):
        """Tez yordam chaqirish metodi"""
        if self.status != self.Status.PENDING:
            raise ValueError("Faqat 'Jarayonda' bo'lgan holaydagina tez yordam chaqirish mumkin")

        self.ambulance_requested = True
        self.status = self.Status.IN_PROGRESS

        if ambulance:
            ambulance.mark_on_duty(location=self.patient.address)
            self.ambulance = ambulance  # agar Emergency modelda ambulance ForeignKey bo'lsa
        self.save()

        Notification.send_notification(
            recipient=self.patient,
            message="🚑 Tez yordam sizning manzilingizga yo'l oldi!",
            notification_type="emergency"
        )
        return True

    class Meta:
        verbose_name = _("Jiddiy holat")
        verbose_name_plural = _("Jiddiy holatlar")
        ordering = ['-created_at']


class Ambulance(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', _('Mavjud')
        ON_DUTY = 'on_duty', _('Xizmatda')
        UNAVAILABLE = 'unavailable', _('Mavjud emas')

    plate_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Davlat raqami")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        verbose_name=_("Holati")
    )
    current_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Joriy manzil")
    )

    def __str__(self):
        return f"🚑 {self.plate_number} - {self.get_status_display()}"

    class Meta:
        verbose_name = _("Tez yordam")
        verbose_name_plural = _("Tez yordamlar")
        ordering = ['status', 'plate_number']
