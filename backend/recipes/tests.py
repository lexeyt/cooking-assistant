from django.test import TestCase

from recipes.models import Ingredient
from users.models import User


class ModelsSmokeTests(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='vi')
        self.salt = Ingredient.objects.create(
            name='salt', measurement_unit='pood')

    def test_Create_Ingredient(self):
        Ingredient.objects.create(
            name='Sugar', measurement_unit='gr')
