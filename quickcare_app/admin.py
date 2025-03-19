from django.contrib import admin
from .models import Doctor, Patient, Notification, Queue, Emergency, Room, Department
from user.models import User


admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Notification)
admin.site.register(Queue)
admin.site.register(Emergency)
admin.site.register(Room)
admin.site.register(Department)
