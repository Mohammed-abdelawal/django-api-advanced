from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
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
        Ingredient.objects.create(user=self.user, name='Ubuntu')

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

        Ingredient.objects.create(user=user2,name='testeer32')
        ingredient = Ingredient.objects.create(user=self.user,name='testeer32')
        
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'],ingredient.name)

        
