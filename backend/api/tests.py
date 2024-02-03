from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from recipes.models import (Ingredient, Tag, RecipeIngredient, Recipe,
                            Favorite, ShoppingCart)
from users.models import Subscribe

User = get_user_model()


class UsersTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.client_non_auth = APIClient()
        self.client_auth = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@email.ru',
            first_name='first_name1',
            last_name='last_name1',
            password='dghbdrtyu$%6reG')
        token = Token.objects.get_or_create(user=self.user1)
        self.client_auth.force_authenticate(user=self.user1,
                                            token=token)

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@email.ru',
            first_name='first_name2',
            last_name='last_name2')
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@email.ru',
            first_name='first_name3',
            last_name='last_name3')

        self.salt = Ingredient.objects.create(
            name='Salt',
            measurement_unit='kg',
        )
        self.recipe = Recipe.objects.create(
            name='soup',
            author=self.user2,
            text='some_text',
            cooking_time=1
        )
        self.tag_black = Tag.objects.create(name='black', slug='black')
        self.recipe.tags.add(self.tag_black)

        self.ingredient_recipe = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=100,
        )
        self.recipe2 = Recipe.objects.create(
            name='red soup',
            author=self.user2,
            text='some_text',
            cooking_time=1
        )
        self.recipe2.tags.add(self.tag_black)

        RecipeIngredient.objects.create(
            recipe=self.recipe2,
            ingredient=self.salt,
            amount=100,
        )

    def test_paginatied_users_list(self):
        url = reverse('users-list')
        params = {
            "page": 2,
            "limit": 2,
        }
        resp = self.client_auth.get(url, data=params)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['username'],
                         self.user3.username)

    def test_register_new_user(self):
        url = reverse('users-list')
        params = {
            "email": "vpupkin@yandex.ru",
            "username": "vasyapupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "dfkgjmbFDG5er#$%"
            }

        resp = self.client_non_auth.post(url, data=params)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=params['email']).exists())

    def test_users_detail(self):
        url = reverse('users-detail', args=(self.user1.id,))

        resp = self.client_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_users_me(self):
        url = reverse('users-me')

        resp = self.client_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        url = reverse('users-set-password')
        params = {
            "new_password": "dflgvjm56456@$%r",
            "current_password": "dghbdrtyu$%6reG",
        }
        resp = self.client_auth.post(url, data=params)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_subscriptions(self):
        url = reverse('users-subscribe', args=(self.user2.pk,))
        params = {
            "recipes_limit": 1,
        }
        resp = self.client_auth.post(url, data=params)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data['recipes']), 1)
        self.assertEqual(resp.data['recipes_count'], 2)
        self.assertTrue(resp.data['is_subscribed'])

        url = reverse('users-subscriptions')
        params = {
            "page": 1,
            "limit": 10,
            "recipes_limit": 1,
        }
        resp = self.client_auth.get(url, data=params)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)

        url = reverse('users-subscribe', args=(self.user2.pk,))
        resp = self.client_auth.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Subscribe.objects.all()), 0)


class IngredientTestCase(TestCase):

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
        self.tag = Tag.objects.create(name='Завтрак',
                                      color='#E26C2D',
                                      slug='breakfast')

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
            text='some_text',
            cooking_time=1
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
            "cooking_time": 1,
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
            "cooking_time": 1,
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
            text='some_text',
            cooking_time=1
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


class ShoppingCartTestCase(TestCase):

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
            text='some_text',
            cooking_time=1
        )
        self.tag_black = Tag.objects.create(name='black', slug='black')
        self.recipe.tags.add(self.tag_black)

        self.ingredient_recipe = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.salt,
            amount=100,
        )

    def test_ShoppingCart(self):
        url = reverse('recipes-shopping-cart', args=(self.recipe.pk,))

        resp = self.client_auth.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ShoppingCart.objects.all()), 1)

        resp = self.client_auth.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse('recipes-download-shopping-cart')
        resp = self.client_auth.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        url = reverse('recipes-shopping-cart', args=(self.recipe.pk,))
        resp = self.client_auth.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(ShoppingCart.objects.all()), 0)
