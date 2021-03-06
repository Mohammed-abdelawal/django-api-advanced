from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTest(TestCase):
    """Test Public Tags Api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login required to view tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authentication user tags api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='myemail@gmail.com',
            password='mygoodpass',
            name='mohammed tester'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_user_tags(self):
        """Test that tags returned are for authenticated user"""

        user2 = get_user_model().objects.create_user(
            email='mymailtester@fake2.com',
            password='mysecondpassshit',
            name='name2 assholes'
        )
        Tag.objects.create(user=user2, name='dskhdks')
        Tag.objects.create(user=user2, name='dskhwserwdks')
        tag = Tag.objects.create(user=self.user, name='dskwewqqs')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'tgname aaa'}
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid data"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtering tags by assigned recipe"""
        tag1 = Tag.objects.create(user=self.user, name='tag 1 unyted')
        tag2 = Tag.objects.create(user=self.user, name='tag 2 7amada')
        rec = Recipe.objects.create(
            title='my title recipe',
            time_minutes=21,
            price=4.00,
            user=self.user,
        )
        rec.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='2y 7aga')
        Tag.objects.create(user=self.user, name='libch')
        recipe1 = Recipe.objects.create(
            user=self.user,
            time_minutes='5',
            price=3.0,
            title='my title for rec 1'
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            user=self.user,
            time_minutes='5',
            price=4.0,
            title='second title for potato'
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
