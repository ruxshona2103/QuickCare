from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from quickcare_app.models import Emergency, Ambulance
from quickcare_app.serializers import EmergencySerializer, AmbulanceSerializer


class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'current_location']
    search_fields = ['plate_number']
    ordering_fields = ['id', 'status']

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Manzil'),
                'emergency_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Favqulodda holat IDsi')
            },
            required=['location']
        ),
        responses={200: AmbulanceSerializer}
    )
    @action(detail=True, methods=['post'])
    def send_ambulance(self, request, pk=None):
        ambulance = self.get_object()
        if ambulance.status != 'available':
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

        emergency_id = request.data.get('emergency_id')
        if emergency_id:
            emergency = get_object_or_404(Emergency, id=emergency_id)
            emergency.ambulance = ambulance
            emergency.status = 'in_progress'
            emergency.save()

        ambulance.status = 'on_duty'
        ambulance.current_location = location
        ambulance.save()

        return Response(self.get_serializer(ambulance).data)

    @swagger_auto_schema(responses={200: AmbulanceSerializer})
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        ambulance = self.get_object()
        ambulance.status = 'available'
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @swagger_auto_schema(responses={200: AmbulanceSerializer})
    @action(detail=True, methods=['post'])
    def mark_unavailable(self, request, pk=None):
        ambulance = self.get_object()
        ambulance.status = "unavailable"
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Yangi manzil'),
            },
            required=['location']
        ),
        responses={200: AmbulanceSerializer}
    )
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

    @swagger_auto_schema(responses={200: EmergencySerializer})
    @action(detail=True, methods=['post'])
    def request_ambulance(self, request, pk=None):
        emergency = self.get_object()

        if emergency.status != 'pending':
            return Response(
                {'detail': "Faqat 'pending' holatidagi chaqiruvlar uchun tez yordam chaqirish mumkin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if emergency.ambulance_requested:
            return Response(
                {'detail': "Bu holat uchun allaqachon tez yordam chaqirilgan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        emergency.request_ambulance()
        return Response(self.get_serializer(emergency).data)

    @swagger_auto_schema(responses={200: EmergencySerializer})
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        emergency = self.get_object()

        if emergency.status == 'resolved':
            return Response(
                {'detail': 'Bu holat allaqachon hal qilingan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        emergency.status = 'resolved'
        emergency.save()

        if hasattr(emergency, 'ambulance') and emergency.ambulance:
            emergency.ambulance.status = 'available'
            emergency.ambulance.save()

        return Response(self.get_serializer(emergency).data)