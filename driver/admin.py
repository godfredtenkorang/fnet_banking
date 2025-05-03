from django.contrib import admin
from .models import MileageRecord, FuelRecord, Expense, OilChange, Notification

# Register your models here.
admin.site.register(MileageRecord)
admin.site.register(FuelRecord)
admin.site.register(Expense)
admin.site.register(Notification)



class OilChangeAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'date', 'mileage', 'cost')
    list_filter = ('vehicle', 'date')


admin.site.register(OilChange, OilChangeAdmin)