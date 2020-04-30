from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    recipe_defaults = {
        'title': 'simple ricepi shot',
        'time_minutes': 10,
        'price': 5.0
    }
    recipe_defaults.update(params)

    return Recipe.objects.create(user=user, **recipe_defaults)


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test for authenticated recipe Api access and operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testato@gmail.com',
            password='mypassass'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test recipes retrived"""
        sample_recipe(self.user)
        sample_recipe(self.user, title='7a7a.com')

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_limited_user_recipes(self):
        """Test recipes are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='ass@gmail.com',
            password='mypass'
        )

        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
