from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeListSerializer, TagSerializer,
                             FavoriteSerializer, RecipeCreateUpdateSerializer)
from recipes.models import Ingredient, Recipe, Tag, Favorite

from .filters import IngredientFilter


class CustomPagination(PageNumberPagination):
    """Не забываем про паджинатор

    Причем кастомный, т.к. там ожидается параметра limit."""
    page_size_query_param = 'limit'


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', ]
    permission_classes = (IsOwnerOrReadOnly, )
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    # def get_queryset(self):
    #     qs = Recipe.objects.add_user_annotations(self.request.user.pk)
    #
    #     # Фильтры из GET-параметров запроса, например.
    #     author = self.request.query_params.get('author', None)
    #     if author:
    #         qs = qs.filter(author=author)
    #
    #     return qs


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly, ]


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, ]
