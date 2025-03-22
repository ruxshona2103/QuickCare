from dis import code_info
from random import choices

from rest_framework import serializers
from quickcare_app.models import Queue, Doctor, Patient, Notification, Room
from .doctor_patient import DoctorSerializer, PatientSerializer
from .staff_serializer import RoomSerializer
from django.utils.timezone import now


class QueueSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor'
    )
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        write_only=True,
        source='room'
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    waiting_time = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = [
            'id', 'patient', 'doctor', 'room',
            'patient_id', 'doctor_id', 'room_id',
            'position', 'status', 'status_display',
            'created_at', 'waiting_time'
        ]
        read_only_fields = ['position', 'created_at']

    def get_waiting_time(self, obj):
        if obj.status == 'waiting':
            waiting_minutes = (now() - obj.created_at).total_seconds() // 60
            return int(waiting_minutes)
        return 0

    def validate(self, data):
        """
        Custom validation to ensure:
        1. Doctor is available
        2. Patient doesn't already have an active queue
        """

        patient = data.get('patient')
        if Queue.objects.filter(
                patient=patient,
                status__in=['waiting', 'in_progress']
        ).exists():
            return serializers.ValidationError(
                {"patient": "Bu bemor allaqachon navbatda turibti."}
            )
        doctor = data.get('doctor')
        active_patients_count = Queue.objects.filter(
            doctor=doctor,
            status__in=['waiting', 'in_progress']
        ).count()

        if active_patients_count >= 20:
            raise serializers.ValidationError(
                {"doctor": "Ushbu shifokorning bir kunlik qabuli limitiga yetdi! "}
            )
        return data

    def create(self, validated_data):
        patient = validated_data.get('patient')
        doctor = validated_data.get('doctor')
        room = validated_data.get('room')

        queue = Queue.add_patient_to_queue(patient, doctor)

        if queue and room :
            queue.room = room
            queue.save()

        if not queue:
            raise serializers.ValidationError(
                {"non_field_errors": "qabul vaqti tugadi. Iltimos ertaga qayta urinib ko'ring"}
            )
        return queue

    def update(self, instance, validated_data):
        """
        Custom update method to handle status changes and notifications
        """
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        if old_status != new_status:
            if new_status == 'canceling' and old_status == 'waiting':
                instance.cancel_queue()
                return instance

            if new_status == 'in_progress' and old_status == 'waiting':
                Notification.send_notification(
                    recipient=instance.patient,
                    message=f"🔔 Hurmatli {instance.patient.user.username}, hozir sizning navbatingiz. Iltimos, {instance.room.room_number} xonaga kiring.",
                    notification_type='queue_update'
                )

            if new_status == 'completed' and old_status == 'in_progress':
                next_queue = Queue.objects.filter(
                    doctor = instance.doctor,
                    status = 'waiting'
                ).order_by('position').first()
                if next_queue:
                    Notification.send_notification(
                        recipient=next_queue.patient,
                        message = f"🔔 Hurmatli {next_queue.patient.user.username}, tayyorlaning, sizning navbatingiz yaqinlashmoqda.",
                        notification_type='queue_update'
                    )


            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance

class QueueListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Queue
        fields = [
            'id', 'patient_name', 'doctor_name',
            'position', 'status', 'status_display',
            'created_at'
        ]

    def get_patient_name(self, obj):
        if obj.patient.user.first_name:
            return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
        return obj.patient.user.username

    def get_doctor_name(self, obj):
        if obj.doctor.user.first_name:
            return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"
        return obj.doctor.user.username


class QueueActionSerializer(serializers.ModelSerializer):
    """ Cancel, Complete amallari uchun yaratilgan serializer"""
    action = serializers.CharField(choices=['cancel', 'start','complete'])

    def validate(self, data):
        queue = self.context.get('queue')
        action = data.get('action')

        if not queue:
            raise serializers.ValidationError("Navbat topilmadi!")

        if action == 'cancel' and queue.status != 'waiting':
            raise serializers.ValidationError("Faqat kutayotganlargina o'z navbatni bekor qilishi mumkin")

        if action == 'start' and queue.status != 'waiting':
            raise serializers.ValidationError("Faqat kutayotganlar o'z navbatini boshlashi mumkun!")

        if action == "complete" and queue.status != "waiting":
            raise serializers.ValidationError("Faqat kutayotganlar o'z navbatini tugatihsi mumkun!")

        return data












