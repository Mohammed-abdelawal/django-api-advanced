from django.test import TestCase
from core import models
from django.contrib.auth import get_user_model
# Create your tests here.


def sample_user(email='te@se.co', password='mypass', name='name'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name
    )


class ModelsTest(TestCase):

    """ Test Models logic and actions """

    def test_create_user_with_email(self):
        """ Test saving user with email successful """
        email = 'testuser@email.com'
        test_password = 'TestPass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=test_password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(test_password))

    def test_email_normmalize(self):
        """ make the email narmalize and this shit """
        email = 'mohammed@GmAiL.CoM'
        my_pass = 'test21Test'

        user = get_user_model().objects.create_user(
            email=email,
            password=my_pass
        )

        self.assertEqual(email.lower(), user.email)

    def test_user_creation_without_email(self):
        """ make sure if user create user with out email will raise error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='dksl'
            )

    def test_create_super_user_shit(self):
        """ Check Creating Super User """
        user = get_user_model().objects.create_superuser(
            email='assholeAdmin@shitmail.com',
            password='testPass1234'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """Test Tag rep"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string rep"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)
