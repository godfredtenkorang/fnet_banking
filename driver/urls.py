from django.urls import path
from . import views

urlpatterns = [
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('mileage/', views.mileage, name='mileage'),
    path('mileage-record/', views.add_mileage, name='mileage_record'),
    path('view-mileage-record/', views.view_mileage, name='view_mileage_record'),
    path('update-mileage-record/<int:mileage_id>/', views.update_mileage, name='update_mileage_record'),
    path('fuel-record/', views.add_fuel, name='fuel_record'),
    path('view-fuel-record/', views.view_fuel, name='view_fuel_record'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('view-expense-record/', views.view_expense, name='view_expense_record'),
    
    path('vehicle/<int:vehicle_id>/maintenance/', views.vehicle_maintenance, name='vehicle_maintenance'),
    path('vehicle/<int:vehicle_id>/record-oil-change/', views.record_oil_change, name='record_oil_change'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]