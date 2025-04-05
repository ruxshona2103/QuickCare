from rest_framework import viewsets
from rest_framework.response import Response
from quickcare_app.models import Department, Room
from quickcare_app.serializers import DepartmentSerializer, RoomSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    # Qo'shimcha xususiyatlar yoki metodlar qo'shish mumkin
    # Masalan, bo'lim nomi bo'yicha filtrlash:
    def get_queryset(self):
        department_name = self.request.query_params.get('name', None)
        if department_name is not None:
            return Department.objects.filter(name__icontains=department_name)
        return Department.objects.all()

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    # Qo'shimcha metodlar yoki xususiyatlar
    # Masalan, xona bo'limi bo'yicha filtrlash:
    def get_queryset(self):
        department = self.request.query_params.get('department', None)
        if department is not None:
            return Room.objects.filter(department__name=department)
        return Room.objects.all()

