from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTest(TestCase):
    """  """

    def setUp(self):
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            'a7mos@Dmail.com',
            'passPass1'
        )
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create_user(
            'user2@Dmail.com',
            'passPass2',
            name='test user fill name')

    def test_users_listed(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_edit_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
