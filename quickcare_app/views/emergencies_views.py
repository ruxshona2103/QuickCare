from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from quickcare_app.models import Emergency, Ambulance, Doctor
from quickcare_app.serializers import EmergencySerializer, AmbulanceSerializer
from quickcare_app.permissions import IsAuthenticated


class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status','current_location']
    search_fields = ['plate_number']
    ordering_fields = ['id','status']

    @action(detail=True, methods=['get'])
    def dispatch(self, request, pk=None):
        ambulance = self.get_object()
        if ambulance.status != Ambulance.STATUS_AVALIABLE:
            return Response(
                {'detail':"Tez yordam jo'natish uchun mavjud emas!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        location = request.data('location')
        if not location:
            return Response(
                {"detail":"Manzil kiritilishi kerak!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ambulance.status = "on_duty"
        ambulance.current_location = location
        ambulance.save()

        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def mark_avaliable(self, request, pk=None):
        ambulance =self.get_object()
        ambulance.status = 'avaliable'
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def mark_unavaliable(self, request, pk=None):
        ambulance = self.get_object()
        ambulance.status = "unavaliable"
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        ambulance = self.get_object()
        location = request.data.get('location')
        if not location:
            return Response(
                {"detail":"Manzil kiritilishi kerak!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        ambulance.current_location = location
        ambulance.save()
        return Response(self.get_serializer(ambulance).data)


class EmergencyViewSet(viewsets.ModelViewSet):
    queryset = Emergency.objects.all()
    serializer_class = EmergencySerializer
    permission_classes = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'ambulance_requested','created_at']
    search_fields = ['description','patient__full_name','doctor__full_name']
    ordering_fields = ['created_at','status']

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    @action(detail=True, methods=['post'])
    def assign_doctor(self, request, pk=None):
        """Assign a doctor to an emergency"""
        emergency = self.get_object()
        doctor_id = request.data.get('doctor_id')

        if not doctor_id:
            return Response(
                {"detail": "Doctor ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"detail": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update emergency with doctor
        emergency.doctor = doctor
        emergency.save()

        return Response(self.get_serializer(emergency).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of an emergency"""
        emergency = self.get_object()
        status_value = request.data.get('status')

        if not status_value:
            return Response(
                {"detail": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if status is valid
        valid_statuses = [choice[0] for choice in Emergency._meta.get_field('status').choices]
        if status_value not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Choose from: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update emergency status
        emergency.status = status_value
        emergency.save()

        return Response(self.get_serializer(emergency).data)

    @action(detail=True, methods=['post'])
    def request_ambulance(self, request, pk=None):
        """Request an ambulance for an emergency"""
        emergency = self.get_object()

        if emergency.ambulance_requested:
            return Response(
                {"detail": "Ambulance already requested for this emergency"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update emergency and request ambulance
        emergency.ambulance_requested = True
        emergency.save()

        # Call the ambulance request method
        emergency.request_ambulance()

        return Response(self.get_serializer(emergency).data)




