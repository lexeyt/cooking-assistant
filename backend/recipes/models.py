from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .enums import Limits
from .utils import text_relation

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
        validators=[
            MinValueValidator(
                Limits.MIN_VALUE_COOKING_TIME.value,
                message=f'Минимальное значение '
                        f'{Limits.MIN_VALUE_COOKING_TIME.value}'
            )
        ]
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Ingredient in recipes"""
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENT.value,
                message=f'Минимальное количество '
                        f'{Limits.MIN_AMOUNT_INGREDIENT.value}'
            )
        ]
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

    class Meta:
        ordering = ['recipe', 'ingredient']
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецептах'

    def __str__(self):
        return text_relation(self.ingredient, self.recipe, 'в')


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
        default_related_name = 'favorites'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite')
        ]

    def __str__(self):
        return text_relation(self.recipe, self.user, 'в избранном у')


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
        default_related_name = 'shopping_cart'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')
        ]

    def __str__(self):
        return text_relation(self.recipe, self.user, 'в корзине у')
