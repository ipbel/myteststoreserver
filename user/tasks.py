import uuid
from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from user.models import EmailVerification, User


@shared_task
def send_email_verification(user_id):
    user = User.objects.get(id=user_id)
    valid = now() + timedelta(days=2)
    email_creator = EmailVerification.objects.create(code=uuid.uuid4(), user=user, valid=valid)
    email_creator.user_verification_email()
