from django.test import TestCase
from django.urls import reverse ,resolve
from cafe.views import HomeView 


class TestCafeUrls(TestCase):
    def test_HomeView(self):
        url=reverse('cafe:home')
        self.assertEqual(resolve(url).func.view_class,HomeView)


