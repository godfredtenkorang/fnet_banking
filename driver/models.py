from django.db import models
from users.models import Driver, Vehicle
from django.utils import timezone


class MileageRecord(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_mileage = models.PositiveIntegerField()
    end_mileage = models.PositiveIntegerField()

    
    @property
    def mileage_used(self):
        return self.end_mileage - self.start_mileage
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.vehicle} - {self.mileage_used} km"
    
class FuelRecord(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    liters = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    station_name = models.CharField(max_length=100, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.liters}L - {self.amount}"


class Expense(models.Model):
    EXPENSE_TYPES = [
        ('maintenance', 'Maintenance'),
        ('repair', 'Repair'),
        ('toll', 'Toll Fee'),
        ('parking', 'Parking Fee'),
        ('other', 'Other'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.get_type_display()} - {self.amount}"