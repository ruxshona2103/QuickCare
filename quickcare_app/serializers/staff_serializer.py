from rest_framework import serializers
from quickcare_app.models import Department, Room


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)  # Bo'lim nomini ko'rsatish uchun

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'department', 'department_name', 'capacity']
        read_only_fields = ['department_name']


