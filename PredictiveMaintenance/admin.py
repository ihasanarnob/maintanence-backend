from django.contrib import admin
from .models import PredictiveMaintenance

@admin.register(PredictiveMaintenance)
class PredictiveMaintenanceAdmin(admin.ModelAdmin):
    list_display = ("id", "device_name", "brand", "created_at")  # choose fields you want to show
    search_fields = ("device_name", "brand")  # enable search
    list_filter = ("brand",)  # add sidebar filters
