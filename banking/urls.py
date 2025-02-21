from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
      path('dashboard', views.dashboard, name='dashboard'),
      path('signUp', views.signUp, name='signUp'),
      path('customerSupport', views.customerSupport, name='customerSupport'),
      path('request', views.request, name='request'),
    
]
