from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_welcome_email(user_email, username):
    """
    Background task to send a welcome email.
    This runs asynchronously — the API doesn't wait for it to finish.
    """
    send_mail(
        subject='Welcome to our SaaS!',
        message=f'Hi {username}, welcome to our platform!',
        from_email='noreply@example.com',
        recipient_list=[user_email],
        fail_silently=True,
    )
    return f"Email sent to {user_email}"