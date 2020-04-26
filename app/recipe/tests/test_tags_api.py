from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
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
