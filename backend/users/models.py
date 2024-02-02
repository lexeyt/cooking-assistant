
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

MAX_LEN_STRING = 150


class User(AbstractUser):
    """Users model"""

    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=MAX_LEN_STRING,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=MAX_LEN_STRING,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LEN_STRING,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LEN_STRING,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=MAX_LEN_STRING,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

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
            UniqueConstraint(fields=['user', 'author'], name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
