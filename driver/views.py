from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import MileageRecordForm, FuelRecordForm, ExpenseForm, UpdateMileageRecordForm
from .models import MileageRecord, FuelRecord, Expense
from django.db.models import Sum
from django.utils import timezone
from django.db.models import F
from django.contrib import messages


def driver_dashboard(request):
    driver = request.user.driver
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get total mileage for the current month
    monthly_mileage = MileageRecord.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    ).annotate(
        calculated_mileage=F('end_mileage') - F('start_mileage')
    ).aggregate(total=Sum('calculated_mileage'))['total'] or 0
    
    # Get total fuel cost for the current month
    monthly_fuel = FuelRecord.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total_fuel=Sum('amount'))['total_fuel'] or 0
    
    # Get total expenses for the current month
    monthly_expenses = Expense.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0
    
    context = {
        'monthly_mileage': monthly_mileage,
        'monthly_fuel': monthly_fuel,
        'monthly_expenses': monthly_expenses,
    }
   
    return render(request, 'driver/dashboard.html', context)


@login_required
def add_mileage(request):
    driver = request.user.driver
    if request.method == 'POST':
        form = MileageRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.driver = driver
            record.save()
            return redirect('driver_dashboard')
    else:
        form = MileageRecordForm()
        
    context = {
        'form': form,
        'title': 'Add Mileage'
    }
    return render(request, 'driver/record_mileage.html', context)

@login_required
def view_mileage(request):
    driver = request.user.driver
    records = MileageRecord.objects.filter(driver=driver).order_by('-date')
    
    context = {
        'records': records,
        'title': 'View Mileage'
    }
    
    return render(request, 'driver/details/mileage_detail.html', context)

def update_mileage(request, mileage_id):
    
    mileage = get_object_or_404(MileageRecord, id=mileage_id)
    
    if request.method == 'POST':
        form = UpdateMileageRecordForm(request.POST, instance=mileage)
        if form.is_valid():
            update_mileage = form.save(commit=False)
            update_mileage.save()
            messages.success(request, 'Mileage Updated Successfully!')
            return redirect('view_mileage_record')
        
    else:
        form = UpdateMileageRecordForm(instance=mileage)
    
    context = {
        'mileage': mileage,
        'form': form,
        'title': 'Update Mileage'
    }
    
    return render(request, 'driver/details/update_mileage.html', context)
    
@login_required
def add_fuel(request):
    driver = request.user.driver
    if request.method == 'POST':
        form = FuelRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.driver = driver
            record.save()
            return redirect('driver_dashboard')
    else:
        form = FuelRecordForm()
        
    context = {
        'form': form,
        'title': 'Add Fuel'
    }
    return render(request, 'driver/record_fuel.html', context)


@login_required
def view_fuel(request):
    driver = request.user.driver
    records = FuelRecord.objects.filter(driver=driver).order_by('-date')
    
    context = {
        'records': records,
        'title': 'View Fuel'
    }
    
    return render(request, 'driver/details/fuel_detail.html', context)


@login_required
def add_expense(request):
    driver = request.user.driver
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.driver = driver
            expense.save()
            return redirect('driver_dashboard')
    else:
        form = ExpenseForm()
        
    context = {
        'form': form,
        'title': 'Add Expense'
    }
    return render(request, 'driver/record_expense.html', context)

@login_required
def view_expense(request):
    driver = request.user.driver
    records = Expense.objects.filter(driver=driver).order_by('-date')
    
    context = {
        'records': records,
        'title': 'View Fuel'
    }
    
    return render(request, 'driver/details/expense_detail.html', context)