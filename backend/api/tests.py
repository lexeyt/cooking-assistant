from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from recipes.models import (Ingredient, Tag, RecipeIngredient, Recipe,
                            Favorite)

User = get_user_model()


class UsersTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.client_auth = APIClient()
        self.user = User.objects.create_user(username='user1',
                                             email='user1@email.ru',
                                             first_name='first_name1',
                                             last_name='last_name1',
                                             password='')
        token = Token.objects.get_or_create(user=self.user)
        self.client_auth.force_authenticate(user=self.user,
                                            token=token)

        User.objects.create_user(username='user2',
                                 email='user2@email.ru',
                                 first_name='first_name2',
                                 last_name='last_name2',
                                 password='')

    def test_pagination_users_list(self):
        url = reverse('users-list')
        resp = self.client_auth.get(url)

        params = {
            "page": 3,
            "limit": 2,
        }
        # resp = self.client_auth.get(url)
        # resp = self.client_auth.get(url, data=params)
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        #
        # self.assertEqual(len(resp.results), 1)
        # self.assertEqual(resp.results[0]['username'], user5.username)

    def test_get_filtered_list(self):
        url = reverse('ingredients-list')

        params = {
            "name": "Sug",
        }

        resp = self.client_auth.get(url, data=params)

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], self.sugar.name)

    def test_get_ingredient_detail(self):
        url = reverse('ingredients-detail', args=(self.salt.pk,))

        resp = self.client_non_auth.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.salt.id, resp.data.get('id'))


class IngredientTestCase(TestCase):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()

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
            self.sugar = Ingredient.objects.create(
                name='Sugar',
                measurement_unit='kg',
            )

        def test_get_ingredient_list(self):
            url = reverse('ingredients-list')

            resp = self.client_non_auth.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

            resp = self.client_auth.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

        def test_get_filtered_list(self):
            url = reverse('ingredients-list')

            params = {
                "name": "Sug",
            }

            resp = self.client_auth.get(url, data=params)

            self.assertEqual(len(resp.data), 1)
            self.assertEqual(resp.data[0]['name'], self.sugar.name)

        def test_get_ingredient_detail(self):
            url = reverse('ingredients-detail', args=(self.salt.pk,))

            resp = self.client_non_auth.get(url)

            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(self.salt.id, resp.data.get('id'))


class TagTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.client_non_auth = APIClient()

        self.client_auth = APIClient()
        self.user = User.objects.create_user(username='user')
        token = Token.objects.get_or_create(user=self.user)
        self.client_auth.force_authenticate(user=self.user,
                                            token=token)
        self.tag = Tag.objects.create(name='Завтрак', color='#E26C2D', slug='breakfast')

    def test_get_tag_list(self):
        url = reverse('tags-list')

        resp = self.client_non_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_tag_detail(self):
        url = reverse('tags-detail', args=(self.tag.pk,))

        resp = self.client_non_auth.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.tag.id, resp.data.get('id'))


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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()


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
        self.recipe.tags.add(self.tag_black)

        self.ingredient_recipe = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=100,
        )

    def test_add_favorite(self):
        url = reverse('recipes-favorite', args=(self.recipe.pk,))

        resp = self.client_auth.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Favorite.objects.all()), 1)
        resp = self.client_auth.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.client_auth.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Favorite.objects.all()), 0)
