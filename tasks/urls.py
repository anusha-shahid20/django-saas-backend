from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_backend, name='hello_backend'),
    path('api/projects/', views.ProjectListAPIView.as_view(), name='project-list'),
    path('api/projects/<int:pk>/', views.ProjectDetailAPIView.as_view(), name='project-detail'),
]