import csv
from django.core.management.base import BaseCommand
from main.models import PredictiveMaintenance

class Command(BaseCommand):
    help = "Import PredictiveMaintenance data from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file to import")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                PredictiveMaintenance.objects.create(
                    brand = row['Brand'],
model = row['Model'],
os = row['OS'],
device_age = row['Device Age'],
battery_health = row['Battery Health'],
battery_cycle_count = row['Battery Cycle Count'],
fast_charging = row['Fast Charging'],
charges_overnight = row['Charges Overnight'],
storage_capacity = row['Storage Capacity'],
ram_capacity = row['RAM Capacity'],
storage_usage = row['Storage Usage'],
ram_usage = row['RAM Usage'],
overheating = row['Overheating'],
drop_history = row['Drop History'],
water_damage = row['Water Damage'],
sensor_issues = row['Sensor Issues'],
battery_bulging = row['Battery Bulging'],
screen_cracked = row['Screen Cracked'],
buttons_not_working = row['Buttons Not Working'],
screen_time = row['Screen Time'],
charge_frequency = row['Charge Frequency'],
charge_time = row['Charge Time'],
environment = row['Environment'],
region_temp = row['Region Temp'],
updated_software = row['Updated Software'],
rooted = row['Rooted'],
primary_use = row['Primary Use'],
major_concern = row['Major Concern'],
user_email = row['User Email'],
created_at = row['Created At'],

                )

        self.stdout.write(self.style.SUCCESS(f"Data imported successfully from {csv_file}!"))
