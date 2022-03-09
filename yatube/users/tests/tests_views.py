from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Author')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_namespace_user(self):
        """Namespace обрабатываут HTML."""

        templates_pages_names = {
            'users/signup.html': reverse('users:signup'),
            'users/logged_out.html': reverse('users:logout'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': reverse(
                'users:password_reset'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_namespace_user_change(self):
        """Namespace обрабатываут HTML."""
        response = self.authorized_client.get(reverse(
            'users:password_change'))
        self.assertTemplateUsed(
            response,
            'users/password_change_form.html')

    def test_namespace_user_done(self):
        """Namespace обрабатываут HTML."""
        response = self.authorized_client.get(reverse(
            'users:password_change_done'))
        self.assertTemplateUsed(
            response,
            'users/password_change_done.html')
