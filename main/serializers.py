from rest_framework import serializers
from .models import PredictiveMaintenance


class PredictiveMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictiveMaintenance
        fields = "__all__"


class DeviceInputSerializer(serializers.Serializer):
    ram = serializers.FloatField()
    storage = serializers.FloatField()
    screen_time = serializers.FloatField()
    charging_freq = serializers.FloatField()
    charge_duration = serializers.FloatField()
    region_temp = serializers.FloatField()
    rooted = serializers.IntegerField()
    battery_health = serializers.FloatField()
    charge_cycles = serializers.FloatField()
    overheating = serializers.IntegerField()
    drop_history = serializers.IntegerField()
    water_damage = serializers.IntegerField()
    sensor_issues = serializers.IntegerField()
    battery_bulging = serializers.IntegerField()
    screen_cracked = serializers.IntegerField()
    buttons_not_working = serializers.IntegerField()