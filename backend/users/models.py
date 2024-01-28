from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Invalid username.',
        code='invalid_username'
    )
    username = models.CharField(
        validators=[username_validator],
        max_length=150,
        verbose_name='Логин',
        unique=True)
    password = models.CharField(
        max_length=255,
        verbose_name='Пароль')
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия')
    email = models.EmailField(
        unique=True,
        max_length=150,
        verbose_name='Электронная почта')
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на автора')

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
