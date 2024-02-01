from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

MAX_LEN_STRING = 200

User = get_user_model()


class Ingredient(models.Model):
    """Ingredients for recipes"""
    name = models.CharField(
        max_length=MAX_LEN_STRING,
        verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=MAX_LEN_STRING,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Tags for recipes"""
    name = models.CharField(
        max_length=MAX_LEN_STRING,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LEN_STRING,
        null=True,
        verbose_name='Уникальный слаг',
        unique=True
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name="Цвет в HEX",
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipes model"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Ingredient in recipes"""
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    """Model to add recipes to favorite"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

