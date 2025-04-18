from rest_framework import serializers
from quickcare_app.models import Doctor, Patient
import re
from datetime import date


class DoctorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id',
            'full_name',
            'specialization',
            'phone',
            'department',
            'department_name',
            'room',
            'room_number',
            'available'
        ]

    def validate_phone(self, value):
        pattern = re.compile(r"^\+?998\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("❌ Yaroqsiz telefon raqam! Format: +998901234567")
        return value





class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    blood_type_display = serializers.CharField(source='get_blood_type_display', read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ['id', "age", "created_at"]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_age(self, obj):
        if obj.birth_date:
            today = date.today()
            return (
                today.year - obj.birth_date.year
                - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
            )
        return None

    def validate_phone(self, value):
        pattern = re.compile(r"^\+?998\d{9}$")
        if not pattern.match(value):
            raise serializers.ValidationError("❌ Yaroqsiz telefon raqam! Format: +998901234567")
        return value

    def create(self, validated_data):
        # Use the model class to create objects, not the serializer class
        patient = Patient.objects.create(**validated_data)
        return patient

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



