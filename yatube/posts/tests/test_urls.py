from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.public_urls = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html'
        }
        cls.not_public_urls = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.public_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_not_public_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.not_public_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_url_uses_correct_template(self):
        """guest URL-адрес использует соответствующий шаблон."""
        for url, template in self.not_public_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertNotEqual(response, template)

    def test_url_exists_at_desired_location_guest(self):
        for url in self.public_urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def authorized_test_url_exists_at_desired_location(self):
        for url in self.not_public_urls:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_returns_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
