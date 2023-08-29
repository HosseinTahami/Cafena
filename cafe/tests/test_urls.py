from django.test import TestCase
from django.urls import reverse ,resolve
from cafe.views import HomeView ,SearchView


class TestcafeUrls(TestCase):
    def test_HomeView(self):
        url=reverse('cafe:home')
        self.assertEqual(resolve(url).func.view_class,HomeView)

    def test_SearchView(self):
        url=reverse('cafe:search_results')
        self.assertEqual(resolve(url).func.view_class,SearchView)

