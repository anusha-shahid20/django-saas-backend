from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, AuditLog


@receiver(post_save, sender=Project)
def log_project_change(sender, instance, created, **kwargs):
    """
    Automatically create an AuditLog entry whenever a Project is saved.
    - If created=True  -> action is 'create'
    - If created=False -> action is 'update'
    """
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        user=None,          # We'll set user later if needed
        action=action,
        model_name='Project',
        object_id=instance.id,
    )