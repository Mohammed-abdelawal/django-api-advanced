from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test the public available ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test Login required to access the end point"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngreientApiTests(TestCase):
    """Test Ingredients can be retrived by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@g.com',
            password='my-good-pass',
            name='user name'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='kali')
        Ingredient.objects.create(user=self.user, name='ubuntu')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            email='my2user@gi.com',
            password='passaass',
            name='new usermame'
        )

        Ingredient.objects.create(user=user2, name='testeer32')
        ingredient = Ingredient.objects.create(
            user=self.user, name='testeer32')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """Test creating new ingredient"""
        payload = {'name': 'test nake'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_ingredient(self):
        """Test creating ingredient with invalid data"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by assigned recipe"""
        ing1 = Ingredient.objects.create(user=self.user, name='ing 1 unydted')
        ing2 = Ingredient.objects.create(user=self.user, name='ing 2 7amadda')
        rec = Recipe.objects.create(
            title='my title recipe fdfd',
            time_minutes=21,
            price=4.00,
            user=self.user,
        )
        rec.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ing = Ingredient.objects.create(user=self.user, name='2y 7aga')
        Ingredient.objects.create(user=self.user, name='libch')
        recipe1 = Recipe.objects.create(
            user=self.user,
            time_minutes='5',
            price=3.0,
            title='my title for rec 1'
        )
        recipe1.ingredients.add(ing)
        recipe2 = Recipe.objects.create(
            user=self.user,
            time_minutes='5',
            price=4.0,
            title='second title for potato'
        )
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
