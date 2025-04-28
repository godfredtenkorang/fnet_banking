from django.urls import path
from . import views

urlpatterns = [
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('mileage-record/', views.add_mileage, name='mileage_record'),
    path('view-mileage-record/', views.view_mileage, name='view_mileage_record'),
    path('fuel-record/', views.add_fuel, name='fuel_record'),
    path('view-fuel-record/', views.view_fuel, name='view_fuel_record'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('view-expense-record/', views.view_expense, name='view_expense_record'),
]