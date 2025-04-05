from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework.exceptions import ValidationError

from quickcare_app.models import Emergency, Ambulance, Doctor
from quickcare_app.serializers import EmergencySerializer, AmbulanceSerializer


class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'current_location']
    search_fields = ['plate_number']
    ordering_fields = ['id', 'status']

    @action(detail=True, methods=['post'])
    def send_ambulance(self, request, pk=None):  # dispatch o'rniga send_ambulance deb o'zgartirildi
        ambulance = self.get_object()
        if ambulance.status != Ambulance.STATUS_AVAILABLE:  # STATUS_AVALIABLE -> STATUS_AVAILABLE
            return Response(
                {'detail': "Tez yordam jo'natish uchun mavjud emas!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        location = request.data.get('location')
        if not location:
            return Response(
                {"detail": "Manzil kiritilishi kerak!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ambulance.status = "on_duty"
        ambulance.current_location = location
        ambulance.save()

        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):  # avaliable -> available
        ambulance = self.get_object()
        ambulance.status = 'available'  # avaliable -> available
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def mark_unavailable(self, request, pk=None):  # unavaliable -> unavailable
        ambulance = self.get_object()
        ambulance.status = "unavailable"  # unavaliable -> unavailable
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        ambulance = self.get_object()
        location = request.data.get('location')
        if not location:
            return Response(
                {"detail": "Manzil kiritilishi kerak!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ambulance.current_location = location
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)


class EmergencyViewSet(viewsets.ModelViewSet):
    queryset = Emergency.objects.all()
    serializer_class = EmergencySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'ambulance_requested', 'created_at']
    search_fields = ['description', 'patient__full_name', 'doctor__full_name']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Sana filtri uchun parametrlarni olish
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        date_format = "%Y-%m-%d"

        if start_date:
            try:
                start_date = make_aware(datetime.strptime(start_date, date_format))
                queryset = queryset.filter(created_at__gte=start_date)
            except ValueError:
                raise ValidationError({"start_date": "Noto'g'ri sana formati. YYYY-MM-DD formatida kiriting."})

        if end_date:
            try:
                end_date = make_aware(datetime.strptime(end_date, date_format))
                queryset = queryset.filter(created_at__lte=end_date)
            except ValueError:
                raise ValidationError({"end_date": "Noto'g'ri sana formati. YYYY-MM-DD formatida kiriting."})

        return queryset


