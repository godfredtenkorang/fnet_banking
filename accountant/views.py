from django.shortcuts import redirect, render
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test, login_required

from accountant.forms import TransactionForm
from accountant.models import Transaction
from django.utils import timezone
from datetime import datetime

from users.views import admin_dashboard




# def admin_dashboard(request):
    # current_month = timezone.now().month
    # current_year = timezone.now().year
    
    # # Monthly totals
    # monthly_income = Transaction.objects.filter(
    #     transaction_type='income',
    #     date__month=current_month,
    #     date__year=current_year
    # ).aggregate(total=Sum('amount'))['total'] or 0
    
    # monthly_expense = Transaction.objects.filter(
    #     transaction_type='expense',
    #     date__month=current_month,
    #     date__year=current_year
    # ).aggregate(total=Sum('amount'))['total'] or 0
    
    # monthly_balance = monthly_income - monthly_expense
    
    # # All transactions for the month
    # transactions = Transaction.objects.filter(
    #     date__month=current_month,
    #     date__year=current_year
    # ).order_by('-date')
    
    # context = {
    #     'monthly_income': monthly_income,
    #     'monthly_expense': monthly_expense,
    #     'monthly_balance': monthly_balance,
    #     'transactions': transactions,
    # }
    # return render(request, 'accountant/dashboard.html')


@login_required
# @user_passes_test(is_accountant)
def accountant_dashboard(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            return redirect('accountant_dashboard')
    else:
        form = TransactionForm()
    
    # Show only accountant's recent transactions
    user_transactions = Transaction.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'transactions': user_transactions,
    }
    return render(request, 'accountant/dashboard.html', context)

# @user_passes_test(is_accountant)
def account_detail(request, account_id):
   
    return render(request, 'accountant/account_detail.html')

def add_expense(request):
    
    return render(request, 'accountant/add_expense.html')