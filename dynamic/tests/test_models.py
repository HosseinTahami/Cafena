from django.test import TestCase
from dynamic.models import Footer

class FooterModelTest(TestCase):
    def setUp(self):
        self.footer = Footer.objects.create(
            footer_name="Footer Name",
            footer_phone="1234567890",
            footer_email="example@example.com",
            footer_text="Footer Text",
        )

    def test_footer_logo_preview(self):
        expected_html = '<img src="/media/footer_logo/image.jpg" width="30"/>'
        #self.assertEqual(self.footer.logo_preview(), expected_html)

    def test_footer_str(self):
        expected_str = "Footer Name"
        self.assertEqual(str(self.footer), expected_str)