import csv
from django.core.management.base import BaseCommand
from main.models import PredictiveMaintenance

class Command(BaseCommand):
    help = "Export PredictiveMaintenance data to CSV"

    def handle(self, *args, **kwargs):
        with open("predictive_maintenance_export.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow([
                "User Email", "Brand", "Model", "OS", "Device Age",
                "Battery Health", "Battery Cycle Count", "Fast Charging", "Charges Overnight",
                "Storage Capacity", "RAM Capacity", "Storage Usage", "RAM Usage",
                "Overheating", "Drop History", "Water Damage", "Sensor Issues",
                "Battery Bulging", "Screen Cracked", "Buttons Not Working",
                "Screen Time", "Charge Frequency", "Charge Time", "Environment",
                "Region Temp", "Updated Software", "Rooted",
                "Primary Use", "Major Concern", "Created At"
            ])

            # Write rows
            for obj in PredictiveMaintenance.objects.all():
                writer.writerow([
                    obj.user_email, obj.brand, obj.model, obj.os, obj.device_age,
                    obj.battery_health, obj.battery_cycle_count, obj.fast_charging, obj.charges_overnight,
                    obj.storage_capacity, obj.ram_capacity, obj.storage_usage, obj.ram_usage,
                    obj.overheating, obj.drop_history, obj.water_damage, obj.sensor_issues,
                    obj.battery_bulging, obj.screen_cracked, obj.buttons_not_working,
                    obj.screen_time, obj.charge_frequency, obj.charge_time, obj.environment,
                    obj.region_temp, obj.updated_software, obj.rooted,
                    obj.primary_use, obj.major_concern, obj.created_at
                ])

        self.stdout.write(self.style.SUCCESS("✅ Data exported to predictive_maintenance_export.csv"))
