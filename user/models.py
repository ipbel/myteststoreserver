from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True)
    is_verified = models.BooleanField(default=False)


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    valid = models.DateTimeField()

    def __str__(self):
        return f'Email verification for {self.user.email}'

    def user_verification_email(self):
        subject = f'Подтверждение email для {self.user.username}'
        link = reverse('user:email_verify', kwargs={'email': self.user.email, 'code': self.code})
        verify_link = f'{settings.DOMAIN_NAME}{link}'
        send_mail(
            subject=subject,
            message=f"Here is the link for verify your account {verify_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_valid_check(self):
        return False if now() >= self.valid else True
