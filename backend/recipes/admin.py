from django.contrib import admin

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient, Favorite

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
