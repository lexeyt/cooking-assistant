
from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"



