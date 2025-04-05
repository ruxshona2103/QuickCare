from django.contrib import admin
from .models import Doctor, Patient, Notification, Queue, Emergency, Room, Department, Reply, Review, Pharmacy

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Notification)
admin.site.register(Queue)
admin.site.register(Emergency)
admin.site.register(Room)
admin.site.register(Department)
admin.site.register(Review)
admin.site.register(Reply)
admin.site.register(Pharmacy)
