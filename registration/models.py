import datetime
import uuid
from django.core.validators import EmailValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import re
from django.core.exceptions import ValidationError


# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Define a model manager for User model with no username field.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password is not None:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


def validate_name(value):
    if not re.match(r'^[a-zA-Z]+$', value):
        raise ValidationError({"message": "This field should only contain alphabets."})


def validate_password(value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError({"message": "Password must contain at least one uppercase letter."})
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError({"message": "Password must contain at least one special character."})
    if not re.search(r'\d', value):
        raise ValidationError({"message": "Password must contain at least one digit."})


class CustomUser(AbstractUser):
    username_validator = None
    username = models.CharField(max_length=30, null=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128, validators=[validate_password])
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator]
    )
    email_is_verified = models.BooleanField(default=False)
    is_google_login = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return str(self.email)


class ManageOtp(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    otp_code = models.IntegerField()
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    expiry = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.expiry:
            self.expiry = datetime.datetime.now() + datetime.timedelta(seconds=120)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.uuid)


class EmailTracking(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    module_name = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.module_name)
