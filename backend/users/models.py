from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from .constants import (EMAIL_MAX_LEN, USERNAME_MAX_LEN,
                        NAME_MAX_LEN, PASSWORD_MAX_LEN)


class User(AbstractUser):
    """Users model"""

    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=EMAIL_MAX_LEN,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=USERNAME_MAX_LEN,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=NAME_MAX_LEN,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=NAME_MAX_LEN,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=PASSWORD_MAX_LEN,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.username}: {self.first_name} - {self.last_name}'


class Subscribe(models.Model):
    """Subscribe to another user"""

    user = models.ForeignKey(
        User,
        related_name='authors',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
