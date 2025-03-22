from rest_framework import serializers
from quickcare_app.models import Medicine, Pharmacy, PatientMedicine

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"



class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = "__all__"


class PatientMedicineSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patinet.full_name', read_only=True)
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)

    class Meta:
        model = PatientMedicine
        fields = ['id', 'patient', 'patient_name', 'medicine','medicine_name', 'dosage','prescribet_at']



