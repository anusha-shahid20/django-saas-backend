from rest_framework import serializers
from .models import Job, Resume

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['recruiter'] # Automatically sets the recruiter to the logged-in user

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'