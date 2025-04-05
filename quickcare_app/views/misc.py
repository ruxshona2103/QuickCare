from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from quickcare_app.models import Notification, Comment, Reply, Review
from quickcare_app.serializers import NotificationSerializer, CommentSerializer, ReplySerializer, ReviewSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        return Notification.objects.filter(recipient=self.request.user).order_by('-sent_at')

    def perform_create(self, serializer):
        serializer.save(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(is_read=False))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.all().order_by('-created_at')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()

        queryset = super().get_queryset()
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'patient'):
            return Response(
                {"detail": "Faqat bemorlar izoh qoldirishi mumkin"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(author=self.request.user.patient)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all().order_by('-created_at')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()

        queryset = super().get_queryset()
        params = self.request.query_params

        if 'doctor_id' in params:
            queryset = queryset.filter(doctor_id=params['doctor_id'])
        if 'room_id' in params:
            queryset = queryset.filter(room_id=params['room_id'])
        if 'patient_id' in params:
            queryset = queryset.filter(patient_id=params['patient_id'])
        return queryset

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'patient'):
            return Response(
                {"detail": "Faqat bemorlar fikr qoldirishi mumkin"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(patient=self.request.user.patient)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        review = self.get_object()
        replies = Reply.objects.filter(review=review)
        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data)


class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Reply.objects.all().order_by('-created_at')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Reply.objects.none()

        queryset = super().get_queryset()
        params = self.request.query_params

        if 'review_id' in params:
            queryset = queryset.filter(review_id=params['review_id'])
        if 'doctor_id' in params:
            queryset = queryset.filter(doctor_id=params['doctor_id'])
        return queryset

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'doctor'):
            return Response(
                {"detail": "Faqat shifokorlar javob qoldirishi mumkin"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(doctor=self.request.user.doctor)

