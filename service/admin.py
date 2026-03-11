from django.contrib import admin
from .models import BikeService

@admin.register(BikeService)
class BikeServiceAdmin(admin.ModelAdmin):
    list_display = ('model', 'total_km', 'last_service_km', 'phone', 'created_at')
