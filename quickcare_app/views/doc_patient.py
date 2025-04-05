from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from quickcare_app.models import Patient, Doctor
from quickcare_app.serializers import DoctorSerializer, PatientSerializer
from quickcare_app.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsDoctorOrStaff,
    IsOwnerOrDoctor
)


class DoctorViewSet(viewsets.ModelViewSet):
    """Shifokorlar uchun viewset"""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['full_name', 'specialization', 'department_name']
    search_fields = ['full_name', 'specialization']
    ordering_fields = ['full_name', 'specialization']

    def get_permissions(self):
        """
        Ruxsatlarni sozlash:
        - Admin: create, update, delete
        - Doktor: list, retrieve, o'z ma'lumotlarini yangilash
        - Boshqalar: faqat ko'rish
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsDoctorOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def by_specialization(self, request):
        """Mutaxassislik bo'yicha shifokorlarni guruhlash"""
        specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
        result = {}

        for spec in specializations:
            doctors = self.get_queryset().filter(specialization=spec)
            result[spec] = DoctorSerializer(doctors, many=True).data

        return Response(result)

    def get_queryset(self):
        """Doktorlar uchun filtratsiya"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'doctor'):
            queryset = queryset.filter(user=self.request.user)
        return queryset



class PatientViewSet(viewsets.ModelViewSet):
    """Bemorlar uchun viewset"""
    queryset = Patient.objects.all().order_by('created_at')
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['chronic_diseases']
    search_fields = ['full_name', 'address', 'medical_history']
    ordering_fields = ['created_at', 'full_name']

    def get_permissions(self):
        """
        Ruxsatlarni sozlash:
        - Admin: hamma amallar
        - Doktor: list, retrieve (faqat ko'rish)
        - Bemor: o'z ma'lumotlarini yangilash
        """
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrDoctor()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsDoctorOrStaff]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Yangi bemor qo'shish"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Bemor yaratishda foydalanuvchini biriktirish"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def medical_summary(self, request, pk=None):
        """Bemorning tibbiy ma'lumotlarini qisqacha ko'rish"""
        patient = self.get_object()
        if not (request.user.is_staff or
                hasattr(request.user, 'doctor') or
                patient.user == request.user):
            return Response(
                {"detail": "Sizga ruxsat berilmagan"},
                status=status.HTTP_403_FORBIDDEN
            )

        summary = {
            'patient_name': patient.full_name,
            'age': PatientSerializer().get_age(patient),
            'blood_type': patient.get_blood_type_display(),
            'allergies': patient.allergies,
            'chronic_diseases': patient.chronic_diseases,
            'medical_history': patient.medical_history
        }
        return Response(summary)

    def get_queryset(self):
        """Bemorlar ro'yxatini filtratsiya qilish"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'patient'):
            # Bemor faqat o'z ma'lumotlarini ko'rsin
            queryset = queryset.filter(user=self.request.user)
        return queryset

