from django.db.models import Sum

from recipes.models import RecipeIngredient


def ingredients_in_cart(shopping_cart):
    recipes = shopping_cart.values_list('recipe_id', flat=True)
    ingredients = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amount=Sum('amount')
    )
    ingredients_in_cart = 'Shopping list:\n'
    for ingredient in ingredients:
          ingredients_in_cart += (
            f'{ingredient["ingredient__name"]} - {ingredient["amount"]} {ingredient["ingredient__measurement_unit"]}\n'
        )
    return ingredients_in_cart