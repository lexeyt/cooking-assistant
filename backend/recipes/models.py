from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .enums import Limits

User = get_user_model()


class Ingredient(models.Model):
    """Ingredients for recipes"""
    name = models.CharField(
        max_length=Limits.MAX_LEN_INGREDIENT_NAME.value,
        verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=Limits.MAX_LEN_MEASUREMENT_UNIT_NAME.value,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit')
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Tags for recipes"""
    name = models.CharField(
        max_length=Limits.MAX_LEN_TAG_NAME.value,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        max_length=Limits.MAX_LEN_TAG_SLUG.value,
        null=True,
        verbose_name='Уникальный слаг',
        unique=True
    )
    color = ColorField(
        default='#FF0000',
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
        max_length=Limits.MAX_LEN_RECIPE_NAME.value,
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
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        null=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1, message='Минимальное значение 1!')]
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
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Shopping cart model"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
