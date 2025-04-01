from django.urls import path, include
from rest_framework.routers import DefaultRouter

from quickcare_app.views import (DoctorViewSet, PatientViewSet,
                                 EmergencyViewSet, AmbulanceViewSet,
                                 MedicineViewSet, PharmacyViewSet, PatientMedicineViewSet)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'emergency', EmergencyViewSet)
router.register(r'ambulance', AmbulanceViewSet)
router.register(r'medicine', MedicineViewSet)
router.register(r'pharmacy', PharmacyViewSet)
router.register(r'patientmedicine', PatientMedicineViewSet)


urlpatterns = [
    path('', include(router.urls)),

]
