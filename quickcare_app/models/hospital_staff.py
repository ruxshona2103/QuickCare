from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="bo'limlar")
    description = models.TextField()

    class Meta:
        verbose_name = "bo'lim"
        verbose_name_plural = "bo'limlar"

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.IntegerField(verbose_name="xona raqami")
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, verbose_name="tegishli bo'lim")
    capacity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "xona"
        verbose_name_plural = "xonalar"


    def __str__(self):
        return self.room_number

