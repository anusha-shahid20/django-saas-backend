from django.urls import path
from . import views


urlpatterns = [
    path('hello/', views.hello_backend, name='hello_backend'),
]