from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_backend, name='hello_backend'),
    
    # Projects
    path('api/projects/', views.ProjectListAPIView.as_view(), name='project-list'),
    path('api/projects/<int:pk>/', views.ProjectDetailAPIView.as_view(), name='project-detail'),
    
    # Tasks
    path('api/tasks/', views.TaskListAPIView.as_view(), name='task-list'),
    path('api/tasks/<int:pk>/', views.TaskDetailAPIView.as_view(), name='task-detail'),
    path('api/tasks/<int:pk>/status/', views.TaskStatusUpdateAPIView.as_view(), name='task-status-update'),
    
    # Notes
    path('api/notes/', views.NoteListAPIView.as_view(), name='note-list'),
    path('api/notes/<int:pk>/', views.NoteDetailAPIView.as_view(), name='note-detail'),

    # File Upload
    path('api/upload/', views.FileUploadAPIView.as_view(), name='file-upload'),
]