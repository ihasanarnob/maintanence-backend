from django.db import models
# from .devices.models import *

class PredictiveMaintenance(models.Model):
    user_email = models.EmailField(null=True, blank=True)
    # Device Information
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    device_age = models.CharField(max_length=20)  # Matches formData.deviceAge

    # Battery Information
    battery_cycle_count = models.CharField(
        max_length=10
    )  # Matches formData.batteryCycleCount
    battery_health = models.CharField(max_length=10)
    fast_charging = models.CharField(max_length=10)
    charges_overnight = models.CharField(max_length=10)

    # Storage and RAM
    storage_capacity = models.CharField(max_length=100)
    ram_capacity = models.CharField(max_length=100)
    storage_usage = models.CharField(max_length=10)
    ram_usage = models.CharField(max_length=10)

    # Repair History
    previous_repairs = models.JSONField(default=list)
    last_repair_date = models.CharField(max_length=100, blank=True, default="")
    authorized_service = models.CharField(max_length=10, blank=True, default="")
    warranty_status = models.CharField(max_length=10, blank=True, default="")

    # Hardware Condition
    overheating = models.BooleanField(default=False)
    drop_history = models.BooleanField(default=False)
    water_damage = models.BooleanField(default=False)
    sensor_issues = models.BooleanField(default=False)
    battery_bulging = models.BooleanField(default=False)
    screen_cracked = models.BooleanField(default=False)
    buttons_not_working = models.BooleanField(default=False)

    # Usage Behavior
    screen_time = models.CharField(max_length=10)
    charge_frequency = models.CharField(max_length=20)
    charge_time = models.CharField(max_length=20)
    environment = models.CharField(max_length=50)
    region_temp = models.CharField(max_length=10)
    updated_software = models.CharField(max_length=10)
    rooted = models.CharField(max_length=10)

    # mL prediction
    ml_prediction = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Prediction result from ML model"
    )

    ml_confidence = models.JSONField(
        blank=True,
        null=True,
        help_text="Prediction probabilities for each class"
    )

    # Arrays/JSON Fields
    primary_use = models.JSONField(default=list)

    # Additional Information
    major_concern = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model}"

    class Meta:
        ordering = ["-created_at"]

# Payment Transaction Model
class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    tran_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15, blank=True)
    product_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    bank_tran_id = models.CharField(max_length=255, blank=True)
    form_data = models.JSONField(default=dict)  # Store form data for PredictiveMaintenance
    predictive_maintenance = models.ForeignKey(
        PredictiveMaintenance, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tran_id} - {self.status} - {self.amount} BDT"