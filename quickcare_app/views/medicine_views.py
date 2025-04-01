from datetime import datetime, timedelta
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from quickcare_app.models import Medicine, Pharmacy, PatientMedicine, Patient
from quickcare_app.serializers import MedicineSerializer, PharmacySerializer, PatientMedicineSerializer
from quickcare_app.permissions import IsAuthenticated, IsAdminUser, IsAdminUserOrReadOnly


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['usage', 'is_avaliable']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """" Dori hozirda sotuvda bor yoki yo'qligini tekshirish uchun"""
        available_medicine = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(available_medicine, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock_info(self, request, pk=None):
        """Ma'lum bir dorini zaxirada mavjudligi haqida ma'lumot olish uchun """
        medicine = self.get_object()
        pharmacy_data = Pharmacy.objects.filter(medicine=medicine)
        serializer = PharmacySerializer.objects.filter(medicine=medicine)
        return Response(serializer.data)


class PharmacyViewSet(viewsets.ModelViewSet):
    """Farmasevtika modeli uchun viewset"""
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['medicine']
    ordering_fields = ['stock']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Zaxirada 10tadan kam qolgan dorilarni chiqarish uchun """
        low_stock = self.get_queryset().filter(stock__lt=10)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """ Zaxirada qolmagan dorilar uchun"""
        out_of_stock = self.get_queryset().filter(stock=0)
        serializer = self.get_serializer(out_of_stock, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def update_stock(self, request, pk=None):
        """Yangi dorilarni zaxiraga joylash"""
        pharmacy_item = self.get_object()
        quantity = request.data.get('quantity', 0)

        if not quantity:
            return Response(
                {"error" "Zaxirada mavjud emas!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        pharmacy_item.stock += int(quantity)
        pharmacy_item.save()
        serializer = self.get_serializer(pharmacy_item)
        return Response(serializer.data)


class PatiantMedicineViewSet(viewsets.ModelViewSet):
    """Bemor retseptlarini boshqarish uchun viewset"""
    queryset = PatientMedicine.objects.all()
    serializer_class = PatientMedicineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['patient', 'medicine']
    search_fields = ['dosage', 'patient', 'medicine']
    ordering_fields = ['prescribed_at']

    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'medicine')

    def create(self, request, *args, **kwargs):
        """Dori-darmon mavjudligini tekshirish va omborni yangilash uchun create metodini qayta yozish."""
        medicine_id = request.data.get('medicine')
        try:
            medicine = Medicine.objects.get(id=medicine_id, is_available=True)
        except Medicine.DoesNotExist:
            return Response(
                {"error": "Dori Mavjud emas yoki tugagan!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        """Zaxirada dori bor yoki yo'qligini tekshirish"""
        try:
            pharmacy_item = Pharmacy.objects.get(medicine=medicine)
            if pharmacy_item.stock <= 0:
                return Response(
                    {'error': 'Zaxirada bu doridan qolmagan'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            pharmacy_item -= 1
            pharmacy_item.save()
        except Pharmacy.DoesNotExist:
            pass

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def patient_history(self, request):
        """ Ma'lum bir bemorni kasallik tarixini bilish """
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {"error": "Bemor ID raqami kiritilishi kerak!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        patient = get_object_or_404(Patient, id=patient_id)
        prescription = self.get_queryset().filter(patient=patient)
        serializer = self.get_serializer(prescription, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_prescription(self, request):
        """Oxirgi 30 kunlik kasallik vaqorlarini ko'rish"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent = self.get_queryset().filter(prescribed_at__gte=thirty_days_ago)
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)


