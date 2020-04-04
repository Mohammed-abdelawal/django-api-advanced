from django.test import TestCase



def add(x, y):
    """Add two numbers together and return the result"""
    return x + y

class CalcTests(TestCase):

    def test_add_numbers_ok(self):
        """Test that values are added together"""
        self.assertEqual(add(3, 8), 11)

    def add_numbers_notok(self):
        """Test that values are added together"""
        self.assertEqual(add(10, 8), 11)