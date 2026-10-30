from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

class Job(models.Model):
    """
    Model to store Job Descriptions created by Recruiters.
    """
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField() # Stores the Job Description text
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title