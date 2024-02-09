from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import ReadOnly, IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeListSerializer, TagSerializer,
                             ShortRecipeSerializer, RecipeCreateSerializer,
                             UserSerializer, SubscribeSerializer,
                             SubscriptionsSerializer, PasswordSerializer,
                             FavoriteSerializer, ShoppingCartSerializer)
from recipes.models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from users.models import Subscribe

from .filters import IngredientFilter, RecipeFilter
from .utils import ingredients_in_cart
from .paginators import PageNumberPagination

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if not user.check_password(old_password):
            return Response(
                'Неверный пароль',
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status=status.HTTP_200_OK)

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
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribtion(self, request, id):
        get_object_or_404(
            Subscribe,
            user=request.user,
            author=get_object_or_404(User, id=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            ShortRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        FavoriteSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        ).is_valid(raise_exception=True)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ShortRecipeSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        ).is_valid(raise_exception=True)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        cart = ShoppingCart.objects.filter(user=self.request.user)
        file = ingredients_in_cart(cart)
        response = HttpResponse(file, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly, ]
