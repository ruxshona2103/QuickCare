from django.urls import path, include
from rest_framework.routers import DefaultRouter

from quickcare_app.views import (
    DoctorViewSet,PatientViewSet,
    EmergencyViewSet,AmbulanceViewSet,
    MedicineViewSet,PharmacyViewSet,
    PatientMedicineViewSet,QueueViewSet,
    NotificationViewSet,ReplyViewSet,
    ReviewViewSet,CommentViewSet,
    DepartmentViewSet, RoomViewSet
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'emergency', EmergencyViewSet)
router.register(r'ambulance', AmbulanceViewSet)
router.register(r'medicine', MedicineViewSet)
router.register(r'pharmacy', PharmacyViewSet)
router.register(r'patient-medicine', PatientMedicineViewSet)
router.register(r'queue', QueueViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'replies', ReplyViewSet, basename='reply')
router.register(r'departments', DepartmentViewSet)
router.register(r'rooms', RoomViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
