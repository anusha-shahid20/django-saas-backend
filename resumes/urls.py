from django.urls import path
from . import views

urlpatterns = [
    path('api/upload/', views.ResumeUploadAPIView.as_view(), name='resume-upload'),
    path('api/rank/', views.ResumeRankingAPIView.as_view(), name='resume-rank'),
    path('api/jobs/', views.JobListCreateAPIView.as_view(), name='job-list-create'), # New Job API
]