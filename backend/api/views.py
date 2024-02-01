from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeListSerializer, TagSerializer,
                             FavoriteSerializer, RecipeCreateUpdateSerializer)
from recipes.models import Ingredient, Smoke, Recipe, Tag, Favorite


class CustomPagination(PageNumberPagination):
    """Не забываем про паджинатор

    Причем кастомный, т.к. там ожидается параметра limit."""
    page_size_query_param = 'limit'


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']

    def get_queryset(self):
        # Пример, как доставать параметры из url, и использовать их.
        qs = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__istartswith=name)
        return qs.all()


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
    permission_classes = [IsAuthenticated, ]


class FavoriteViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, ]
