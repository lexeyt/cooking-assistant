from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeListSerializer, TagSerializer,
                             FavoriteSerializer, RecipeCreateUpdateSerializer)
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, Favorite

from .filters import IngredientFilter

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    # permission_classes = (IsAdminOrReadOnly,)




    # pagination_class = CustomPagination

    # add_serializer = UserSubscribeSerializer
    # link_model = Subscriptions

    # @action(detail=True, permission_classes=(IsAuthenticated,))
    # def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
    #     """Создаёт/удалет связь между пользователями.
    #
    #     Вызов метода через url: */user/<int:id>/subscribe/.
    #
    #     Args:
    #         request (WSGIRequest): Объект запроса.
    #         id (int):
    #             id пользователя, на которого желает подписаться
    #             или отписаться запрашивающий пользователь.
    #
    #     Returns:
    #         Responce: Статус подтверждающий/отклоняющий действие.
    #     """
    #
    # @subscribe.mapping.post
    # def create_subscribe(
    #     self, request: WSGIRequest, id: int | str
    # ) -> Response:
    #     return self._create_relation(id)
    #
    # @subscribe.mapping.delete
    # def delete_subscribe(
    #     self, request: WSGIRequest, id: int | str
    # ) -> Response:
    #     return self._delete_relation(Q(author__id=id))
    #
    # @action(
    #     methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    # )
    # def subscriptions(self, request: WSGIRequest) -> Response:
    #     """Список подписок пользоваетеля.
    #
    #     Вызов метода через url: */user/<int:id>/subscribtions/.
    #
    #     Args:
    #         request (WSGIRequest): Объект запроса.
    #
    #     Returns:
    #         Responce:
    #             401 - для неавторизованного пользователя.
    #             Список подписок для авторизованного пользователя.
    #     """
    #     pages = self.paginate_queryset(
    #         User.objects.filter(subscribers__user=self.request.user)
    #     )
    #     serializer = UserSubscribeSerializer(pages, many=True)
    #     return self.get_paginated_response(serializer.data)


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
