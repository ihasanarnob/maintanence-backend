from django.contrib import admin

from main.models import PredictiveMaintenance

#for print and export as .csv file
# qs = PredictiveMaintenance.objects.all()
# print(qs)



# Register your models here.
class PredictiveMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('id', "brand", "model", "created_at")
    search_fields = ('name', 'status')

admin.site.register(PredictiveMaintenance, PredictiveMaintenanceAdmin)