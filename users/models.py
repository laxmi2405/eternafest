from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from events.models import Event


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    members = models.IntegerField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.name} booked {self.event.name}"
