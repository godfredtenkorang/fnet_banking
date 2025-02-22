from django.urls import path
from . import views

urlpatterns = [
 path('registerAgent/', views.registerAgent, name='registerAgent'),
 path('myAgent/', views.myAgent, name='myAgent'),
]