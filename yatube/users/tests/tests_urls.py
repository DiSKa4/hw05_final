from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_guest(self):
        """Проверка доступности адресов."""
        templates_url_names = [
            '/auth/logout/',
            '/auth/signup/',
            '/auth/login/'
        ]

        for value in templates_url_names:
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client(self):
        """Проверка доступности адресов."""
        templates_url_names = [
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/'
        ]

        for value in templates_url_names:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_user_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/logged_out.html': '/auth/logout/',
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_user_correct_template_url(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
