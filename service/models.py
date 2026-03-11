

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class BikeService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    model = models.CharField(max_length=100)
    total_km = models.IntegerField()
    last_service_km = models.IntegerField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model
