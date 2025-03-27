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
        source = 'patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor',
        required=False,
        allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Emergency
        fields = [
            'id', 'patient', 'doctor', 'patient_id', 'doctor_id',
            'description', 'status', 'status_display',
            'ambulance_requested', 'created_at'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        emergency = Emergency.objects.create(**validated_data)

        if emergency.ambulance_requested:
            emergency.request_ambulance()
        return emergency

