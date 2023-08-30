from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import Personnel
from accounts.managers import PersonnelManager


class PersonnelManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.personnel = Personnel

    def test_create_user(self):
        user = self.personnel.objects.create_user(
            full_name="test user",
            email="test@email.com",
            phone_number="09121234567",
            password="12345678qQ",
        )
        self.assertIsInstance(user, Personnel)
        self.assertEqual(user.full_name, "test user")
        self.assertEqual(user.email, "test@email.com")
        self.assertEqual(user.phone_number, "09121234567")
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)

    def test_required_fields(self):
        with self.assertRaisesMessage(ValidationError, "User have to have full name!"):
            self.personnel.objects.create_user(
                full_name="",
                email="test@email.com",
                phone_number="09121234567",
                password="12345678qQ",
            )

        with self.assertRaisesMessage(ValidationError, "User have to have email!"):
            self.personnel.objects.create_user(
                full_name="test user",
                email="",
                phone_number="09121234567",
                password="testpassword",
            )

        with self.assertRaisesMessage(
            ValidationError, "User have to have phone_number!"
        ):
            self.personnel.objects.create_user(
                full_name="test user",
                email="test@email.com",
                phone_number="",
                password="testpassword",
            )

    def test_create_superuser(self):
        superuser = self.personnel.objects.create_superuser(
            full_name="test superuser",
            email="test@email.com",
            phone_number="09121234567",
            password="testpassword",
        )
        self.assertIsInstance(superuser, Personnel)
        self.assertEqual(superuser.full_name, "test superuser")
        self.assertEqual(superuser.email, "test@email.com")
        self.assertEqual(superuser.phone_number, "09121234567")
        self.assertTrue(superuser.is_admin)
        self.assertTrue(superuser.is_superuser)
