from django.urls import path
from . import views

urlpatterns = [
    path('customerSupport', views.customerSupport, name='customerSupport'),
   
    
]
