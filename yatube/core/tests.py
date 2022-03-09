from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_404_url_uses_correct_template(self):
        """Страница по адресу /unexisting_page/
        использует шаблон core/404.html"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
