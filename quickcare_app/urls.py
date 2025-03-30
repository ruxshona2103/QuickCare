from django.urls import path, include
from rest_framework.routers import DefaultRouter

from quickcare_app.views import DoctorViewSet, PatientViewSet, EmergencyViewSet, AmbulanceViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'emergency', EmergencyViewSet)
router.register(r'ambulance', AmbulanceViewSet)


urlpatterns = [
    path('', include(router.urls)),

]
