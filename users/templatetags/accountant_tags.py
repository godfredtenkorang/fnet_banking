from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def calculate_balance(income, expense):
    income = income or 0
    expense = expense or 0
    return income - expense