from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from quickcare_app.models import Queue
from quickcare_app.serializers.queue_serializer import (
    QueueSerializer,
    QueueListSerializer,
    QueueActionSerializer
)
from quickcare_app.permissions import (
    IsDoctor,
    IsPatient,
    IsOwnerOrDoctor,
    IsAdminUser,
    IsAuthenticated,
)


class QueueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient queues.

    Provides CRUD operations and additional actions for queue management:
    - list_my_queues: Get queues for the current user (patient or doctor)
    - perform_action: Execute actions on a queue (cancel, start, complete)
    - next_patient: Get the next patient in the queue for a doctor
    """
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'doctor', 'patient', 'room']
    search_fields = ['patient__full_name', 'doctor__full_name']
    ordering_fields = ['position', 'created_at']
    ordering = ['position', 'created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return QueueListSerializer
        elif self.action == 'perform_action':
            return QueueActionSerializer
        return QueueSerializer

    def get_permissions(self):
        """
        Set custom permissions based on the action:
        - create: Patient can create a queue
        - list: Any authenticated user
        - retrieve, update, partial_update: Owner (patient) or assigned doctor
        - destroy: Admin only
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsPatient]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'perform_action']:
            permission_classes = [IsAuthenticated, IsOwnerOrDoctor]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        elif self.action in ['next_patient', 'doctor_statistics']:
            permission_classes = [IsDoctor]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = super().get_queryset()

        # If action is list_my_queues, filter based on user role
        if self.action == 'list_my_queues':
            if hasattr(user, 'patient'):
                return queryset.filter(patient__user=user)
            elif hasattr(user, 'doctor'):
                return queryset.filter(doctor__user=user)
            elif user.is_staff:
                # Staff and admins can see all queues
                return queryset
            return Queue.objects.none()

        return queryset

    @action(detail=False, methods=['get'])
    def list_my_queues(self, request):
        """
        List queues for the current user.
        - For patients: Shows their queues
        - For doctors: Shows queues assigned to them
        """
        queryset = self.get_queryset()

        # Additional filtering by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def perform_action(self, request, pk=None):
        """
        Perform actions on a queue:
        - cancel: Cancel a waiting queue
        - start: Start a waiting queue (change to in_progress)
        - complete: Complete an in-progress queue
        """
        queue = self.get_object()
        serializer = QueueActionSerializer(data=request.data, context={'queue': queue})

        if serializer.is_valid():
            action = serializer.validated_data['action']

            if action == 'cancel':
                if hasattr(request.user, 'patient') and request.user.patient == queue.patient:
                    queue.status = 'cancelled'
                    queue.cancel_queue()
                    return Response({'detail': 'Navbat bekor qilindi.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Faqat bemor o\'z navbatini bekor qilishi mumkin.'},
                                status=status.HTTP_403_FORBIDDEN)

            elif action == 'start':
                if hasattr(request.user, 'doctor') and request.user.doctor == queue.doctor:
                    queue.status = 'in_progress'
                    queue.save()
                    return Response({'detail': 'Qabul boshlandi.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Faqat shifokor qabulni boshlashi mumkin.'},
                                status=status.HTTP_403_FORBIDDEN)

            elif action == 'complete':
                if hasattr(request.user, 'doctor') and request.user.doctor == queue.doctor:
                    queue.status = 'completed'
                    queue.save()
                    return Response({'detail': 'Qabul yakunlandi.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Faqat shifokor qabulni yakunlashi mumkin.'},
                                status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def next_patient(self, request):
        """
        Get the next patient in the queue for the doctor.
        Only available for doctors.
        """
        if not hasattr(request.user, 'doctor'):
            return Response({'detail': 'Faqat shifokorlar uchun.'}, status=status.HTTP_403_FORBIDDEN)

        doctor = request.user.doctor
        next_queue = Queue.objects.filter(
            doctor=doctor,
            status='waiting'
        ).order_by('position').first()

        if next_queue:
            serializer = self.get_serializer(next_queue)
            return Response(serializer.data)
        return Response({'detail': 'Navbatda kutayotgan bemorlar yo\'q.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def doctor_statistics(self, request):
        """
        Get statistics for a doctor's queue.
        - waiting_count: Number of patients waiting
        - in_progress_count: Number of patients currently in progress
        - completed_today: Number of patients completed today
        """
        if not hasattr(request.user, 'doctor'):
            return Response({'detail': 'Faqat shifokorlar uchun.'}, status=status.HTTP_403_FORBIDDEN)

        from django.utils import timezone
        import datetime

        doctor = request.user.doctor
        today = timezone.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        today_start = datetime.datetime.combine(today, datetime.time.min, tzinfo=timezone.get_current_timezone())
        today_end = datetime.datetime.combine(tomorrow, datetime.time.min, tzinfo=timezone.get_current_timezone())

        waiting_count = Queue.objects.filter(doctor=doctor, status='waiting').count()
        in_progress_count = Queue.objects.filter(doctor=doctor, status='in_progress').count()
        completed_today = Queue.objects.filter(
            doctor=doctor,
            status='completed',
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()

        return Response({
            'waiting_count': waiting_count,
            'in_progress_count': in_progress_count,
            'completed_today': completed_today,
            'total_active': waiting_count + in_progress_count
        })

    def perform_create(self, serializer):
        """Custom create to handle additional logic if needed."""
        serializer.save()


