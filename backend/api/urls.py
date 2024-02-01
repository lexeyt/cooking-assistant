from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipesViewSet,
                       TagViewSet, FavoriteViewSet)

v1_router = DefaultRouter()

v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipesViewSet, basename='recipes')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    # Авторизация по токену.
    path('v1/auth/', include('djoser.urls.authtoken')),
]