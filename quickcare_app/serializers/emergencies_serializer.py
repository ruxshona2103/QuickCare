from rest_framework import serializers
from quickcare_app.models import Emergency, Ambulance, Patient, Doctor
from quickcare_app.serializers import PatientSerializer, DoctorSerializer

class AmbulanceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ambulance
        fields = ['id', 'plate_number', 'status', 'status_display', 'current_location']


class EmergencySerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source = 'patient',
        error_messages = {
            'does_not_exist': 'Bunday IDga ega bemor topilmadi.',
            'incorrect_type': 'Noto\'g\'ri ID formati.'
        }
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor',
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'Bunday IDga ega bemor topilmadi.',
            'incorrect_type': 'Noto\'g\'ri ID formati.'
        }
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Emergency
        fields = [
            'id',
            'patient', 'patient_id',
            'doctor', 'doctor_id',
            'description',
            'status', 'status_display',
            'ambulance_requested', 'can_request_ambulance',
            'created_at',
        ]
        read_only_fields = [
            'status_display',
            'created_at',
            'can_request_ambulance'
        ]
        extra_kwargs = {
            'status': {
                'help_text': f"Mavjud statuslar: {','.join([choice[0] for choice in Emergency.Status.choices])}"
            },
            'ambulance_requested': {
                'help_text': 'Agar tez yordam chaqirish kerak bo\'lsa, belgilang'
            }
        }

    def get_can_request_ambulance(self, obj):
        """Tez yordam chaqirish mumkinligini tekshiradi"""
        return obj.status == Emergency.Status.PENDING and not obj.ambulance_requested

    def validate(self, data):
        """Ma'lumotlarni tekshirish"""
        if len(data.get('description', '')) < 10:
            raise serializers.ValidationError(
                {'description': 'Tavsif 10 ta belgidan kam bo\'lmasligi kerak'}
            )

        if data.get('ambulance_requested') and not data.get('patient').address:
            raise serializers.ValidationError(
                {'ambulance_requested': 'Bemorning manzili kiritilmagan. Tez yordam chaqirish uchun manzil kerak.'}
            )

        return data

    def create(self, validated_data):
        """Yangi favqulodda holat yaratish"""
        try:
            emergency = Emergency.objects.create(**validated_data)

            if emergency.ambulance_requested:
                emergency.request_ambulance()
            return emergency
        except Exception as e:
            raise serializers.ValidationError(
                {'non_field_errors': [f'Yaratishda xato yuz berdi: {str(e)}']}
            )

    def update(self, instance, validated_data):
        """Favqulodda holatni yangilash"""
        try:
            instance = super().update(instance, validated_data)

            # Agar status "resolved" ga o'zgartirilsa, tez yordamni bo'shatish
            if instance.status == Emergency.Status.RESOLVED and instance.ambulance:
                instance.ambulance.mark_available()

            return instance
        except Exception as e:
            raise serializers.ValidationError(
                {'non_field_errors': [f'Yangilashda xato yuz berdi: {str(e)}']}
            )