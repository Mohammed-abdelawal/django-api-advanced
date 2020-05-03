from core.models import Recipe, Ingredient, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """return recipe reverse URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='basic tag'):
    """create sample tag object"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='basic ingredient'):
    """create sample ingredient object"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe details"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test create simple recipe"""
        payload = {
            'title': 'my recipe title',
            'time_minutes': 30,
            'price': 5.0
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k in payload.keys():
            self.assertEqual(payload[k], getattr(recipe, k))

    def test_create_recipe_with_tags(self):
        """Test creating a recipr with tags"""
        tag1 = sample_tag(user=self.user, name='myTagOne')
        tag2 = sample_tag(user=self.user, name='myTagTwo')

        payload = {
            'title': 'my new recipe ',
            'time_minutes': 31,
            'price': 25.0,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)

        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_recipe_ingredients(self):
        """Test create recipe with ingredients"""
        ingredient1 = sample_ingredient(
            user=self.user, name='my ingredient name shit')
        ingredient2 = sample_ingredient(user=self.user, name='shit testing')

        payload = {
            'title': 'title for testing f**k',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 23,
            'price': 2.1
        }

        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test Update for existing recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='new tag')

        payload = {
            'title': 'simple ricepi shot',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.data['title'], payload['title'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update(self):
        """Test Update recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghiti title shit',
            'time_minutes': 4,
            'price': Decimal('4.90')
        }
        url = detail_url(recipe.id)

        self.client.put(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.count()
        self.assertEqual(tags, 0)
