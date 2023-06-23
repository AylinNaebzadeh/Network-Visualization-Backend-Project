from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('general_statistical_info/', general_statistical_info, name="get general statistical information"),
]