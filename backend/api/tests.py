from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from recipes.models import (Ingredient, Tag, RecipeIngredient, Recipe,
                            Favorite)

User = get_user_model()


class TestCaseIngredient(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='admin')
        self.ingredient = Ingredient.objects.create(
            name='salt',
            measurement_unit='gr',
        )
        self.client.force_login(user=self.user)

    def test_list(self):
        url = reverse('ingredients-list')
        print(url)
        # /api/v1/ingredients/

        resp = self.client.get(url)

        print(resp.data)
        # [OrderedDict(
        # [('id', 1), ('name', 'salt'), ('measurement_unit', 'gr')])
        # ]


class RecipeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.admin = User.objects.create(username='admin', email='l@l.ru')
        token, _ = Token.objects.get_or_create(user=cls.admin)

        cls.client_admin = APIClient()
        cls.client_admin.force_authenticate(user=cls.admin,
                                            token=cls.admin.auth_token)

    def setUp(self) -> None:
        self.client_non_auth = APIClient()

        self.client_auth = APIClient()
        self.user = User.objects.create_user(username='user')
        token = Token.objects.get_or_create(user=self.user)
        self.client_auth.force_authenticate(user=self.user,
                                            token=token)

        self.salt = Ingredient.objects.create(
            name='Salt',
            measurement_unit='kg',
        )
        self.recipe = Recipe.objects.create(
            name='soup',
            author=self.user,
            text='some_text'
        )
        self.tag_black = Tag.objects.create(name='black', slug='black')
        self.tag_white = Tag.objects.create(name='white', slug='white')

        self.recipe.tags.add(self.tag_black)
        self.recipe.tags.add(self.tag_white)

        self.ingredient_recipe = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=100,
        )

    def test_get_recipe_list(self):
        url = reverse('recipes-list')

        resp = self.client_non_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_recipe_detail(self):
        url = reverse('recipes-detail', args=(self.recipe.pk,))

        resp = self.client_non_auth.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.recipe.id, resp.data.get('id'))

    def test_create_recipe(self):
        url = reverse('recipes-list')
        data = {
            "name": "Медовуха",
            "text": "Сварить",
            "ingredients": [{'id': self.salt.id, 'amount': '22'}, ],
            "tags": [self.tag_white.pk, self.tag_black.pk, ],
            "author": self.user.pk,
        }

        resp = self.client_auth.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_recipe(self):
        url = reverse('recipes-detail', args=(self.recipe.pk,))
        data = {
            "name": "Медовуха",
            "text": "Сварганить",
            "ingredients": [{'id': self.salt.id, 'amount': '21'}, ],
            "tags": [self.tag_white.pk, self.tag_black.pk, ],
            "author": self.user.pk,
        }

        resp = self.client_non_auth.patch(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client_auth.patch(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('name'), data['name'])


class FavoriteTestCase(TestCase):

    def setUp(self) -> None:
        # Создаем клиента, с токеном.
        self.admin = User.objects.create(username='lauren',
                                         email='l@l.ru')
        token, _ = Token.objects.get_or_create(user=self.admin)

        # Авторизируем его.
        self.client_admin = APIClient()
        self.client_admin.force_authenticate(user=self.admin,
                                             token=self.admin.auth_token)

        self.client_auth = Client()
        self.recipe = Recipe.objects.create(
            name='soup',
            author=self.admin,
            text='some_text'
        )
        self.favorite = Favorite.objects.create(
            recipe=self.recipe,
            user=self.admin,
        )

    def test_list(self):
        url = reverse('favorites-list')
        print(url)
        # /api/v1/favorites/

        resp = self.client_admin.get(url)

        print(resp.data)
        print(resp.data[0]['user'])