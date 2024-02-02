from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeListSerializer, TagSerializer,
                             ShortRecipeSerializer, RecipeCreateUpdateSerializer,
                             CustomUserSerializer, SubscribeSerializer, SubscriptionsSerializer)
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, Favorite
from users.models import Subscribe

from .filters import IngredientFilter

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)
        pages = self.paginate_queryset(queryset=queryset)
        serializer = SubscriptionsSerializer(pages,
                                             context={'request': request},
                                             many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, recipe)
        else:
            return self.delete_from(Favorite, request.user, recipe)

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )
    # def shopping_cart(self, request, pk):
    #     if request.method == 'POST':
    #         return self.add_to(ShoppingCart, request.user, pk)
    #     else:
    #         return self.delete_from(ShoppingCart, request.user, pk)
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly, )
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, recipe)
        else:
            return self.delete_from(Favorite, request.user, recipe)

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated]
    # )
    # def shopping_cart(self, request, pk):
    #     if request.method == 'POST':
    #         return self.add_to(ShoppingCart, request.user, pk)
    #     else:
    #         return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, recipe):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже добавлен!'}, status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, recipe):
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'}, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly, ]

