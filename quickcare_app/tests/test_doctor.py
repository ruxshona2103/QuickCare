from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from quickcare_app.models import Doctor, Department, Room
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class DoctorTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            phone_number="+998901234567", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.department = Department.objects.create(name="Kardiologiya")
        self.room = Room.objects.create(room_number="101", floor=1)

        self.doctor = Doctor.objects.create(
            full_name="Shifokor A",
            specialization="Kardiolog",
            phone="+998998887766",
            department=self.department,
            room=self.room,
            available=True
        )

    def test_doctor_list(self):
        url = reverse("doctor-list")  # DRF ViewSet uchun
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_detail(self):
        url = reverse("doctor-detail", args=[self.doctor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_create(self):
        data = {
            "full_name": "Shifokor B",
            "specialization": "Nevrolog",
            "phone": "+998933322211",
            "department": self.department.id,
            "room": self.room.id,
            "available": True,
        }
        url = reverse("doctor-list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_doctor_update(self):
        url = reverse("doctor-detail", args=[self.doctor.pk])
        data = {"available": False}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.available)

    def test_doctor_delete(self):
        url = reverse("doctor-detail", args=[self.doctor.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
