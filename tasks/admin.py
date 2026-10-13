from django.contrib import admin
from .models import Project, Task, Company, UserProfile, AuditLog

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Company)
admin.site.register(UserProfile)
admin.site.register(AuditLog)