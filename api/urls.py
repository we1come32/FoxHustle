from django.urls import path
from . import views

urlpatterns = [
    path('<str:method>', views.getMethod)
]