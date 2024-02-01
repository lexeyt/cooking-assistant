from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField

from recipes.models import (Ingredient, Tag, RecipeIngredient, Recipe,
                            Favorite)

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            # "is_subscribed",
            "password",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('amount', 'name', 'measurement_unit', 'id')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    #image = Base64ImageField()
    # is_favorited = SerializerMethodField(read_only=True)
    # is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            #'is_favorited',
            #'is_in_shopping_cart',
            'name',
            #'image',
            'text',
            #'cooking_time',
        )

    def get_ingredients(self, obj):
        qs = RecipeIngredient.objects.filter(recipe=obj).all()
        return RecipeIngredientSerializer(qs, many=True).data

    # def get_is_favorited(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return user.favorites.filter(recipe=obj).exists()
    #
    # def get_is_in_shopping_cart(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return user.shopping_cart.filter(recipe=obj).exists()


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    def create_ingredients(self, ingredients, recipe):
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(
            create_ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(obj, context=context).data

    class Meta:
        model = Recipe
        fields = ('name', 'ingredients', 'text', 'tags')


class ShortRecipeSerializer(serializers.ModelSerializer):
    #image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            #'image',
            # 'cooking_time'
        )



