from rest_framework import serializers
from .models import PredictiveMaintenance


class PredictiveMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictiveMaintenance
        fields = "__all__"
