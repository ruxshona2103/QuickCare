from rest_framework import serializers
from quickcare_app.models import Notification, Comment, Review, Reply


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source="recipient.username", read_only=True)
    class Meta:
        model = Notification
        fields = ["id", "recipient", "recipient_name", "message", "sent_at", "notification_type"]

    def create(self, validated_data):
        notification = Notification.objects.create(**validated_data)
        return notification


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username")
    doctor_name = serializers.CharField(source="doctor.username")

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'doctor', 'doctor_name', 'text', 'created_at']

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment


class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patients.username")
    doctor_name = serializers.CharField(source="doctor.username")
    room_number = serializers.CharField(source="room.room_number")

    class Meta:
        model = Review
        fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_name', 'room', 'room_number', 'rating', 'comment',
                  'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Reyting 1 dan 5 gacha bo'lgan oralqida belgilanadi")
        return value

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        return review


class ReplySerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.username', read_only=True)  # Shifokorning ismi
    review_id = serializers.IntegerField(source='review.id', read_only=True)  # Sharh ID si

    class Meta:
        model = Reply
        fields = ['id', 'review_id', 'doctor', 'doctor_name', 'response_text', 'created_at']
        read_only_fields = ['created_at']

    def validate_response_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Javob matni bo‘sh bo‘lishi mumkin emas.")
        return value
