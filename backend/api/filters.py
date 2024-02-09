from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return (queryset.filter(favorite__user=self.request.user.id)
                    .filter(favorite__user__isnull=False))
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return (queryset.filter(shoppingcart__user=self.request.user.id)
                    .filter(shoppingcart__user__isnull=False))
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
