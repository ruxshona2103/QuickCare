from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from quickcare_app.models import Patient, Doctor
from quickcare_app.serializers import DoctorSerializer, PatientSerializer
from quickcare_app.permissions import  IsAdminUser, IsAuthenticated


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by('created_at')
    serializer_class = DoctorSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['full_name', 'specialization', 'departmen_name']
    search_fields = ['full_name', 'specialization']
    ordering_fields = ['full_name', 'specialization']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return permission_classes

    @action(detail=False, methods=['get'])
    def by_specialization(self, request):
        specialization = Doctor.objects.filter.values_list('specialization', flat=True).distinct()
        result = {}

        for spec in specialization:
            doctors = self.queryset.filters(specialization=spec)
            result[spec] = DoctorSerializer(doctors, many=True).data

        return Response(result)



class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('created_at')
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['chronic_diseases']
    search_fields = ['full_name', 'address', 'medical_history']
    ordering_fields = ['created_at', 'full_name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def medical_summary(self, request, pk=None):
        """Custom endpoint to get a summary of patient's medical information"""
        patient = self.get_object()
        summary = {
            'patient_name': patient.full_name,
            'age': PatientSerializer().get_age(patient),
            'blood_type': patient.get_blood_type_display(),
            'allergies': patient.allergies,
            'chronic_diseases': patient.chronic_diseases,
            'medical_history': patient.medical_history
        }
        return Response(summary)

