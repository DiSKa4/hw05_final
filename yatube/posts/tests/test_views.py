from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.public_urls = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse(
                'posts:group_list', kwargs={
                    'slug': 'test-slug'}),
                'posts/group_list.html'),
            (reverse(
                'posts:profile', kwargs={
                    'username': 'Author'}),
                'posts/profile.html'),
            (reverse(
                'posts:post_detail', kwargs={
                    'post_id': cls.post.id}),
                'posts/post_detail.html')
        )
        cls.not_public_urls = (
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse(
                'posts:post_edit', kwargs={
                    'post_id': cls.post.id}),
                'posts/create_post.html')
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.public_urls + self.not_public_urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_fields(self, post):
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)

    def test_correct_template(self):
        """Шаблон сформирован с правильным контекстом."""
        for reverse_name, template in self.public_urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                if 'page_obj' in response.context:
                    post = response.context.get('page_obj')[0]
                else:
                    post = response.context.get('post')
                self.check_fields(post)

    def test_create_edit_post(self):
        """Шаблон not_public сформирован с правильным контекстом"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ChoiceField,
            'image': forms.fields.ImageField
        }
        for reverse_name, _ in self.not_public_urls:
            for field_name, expected in form_fields.items():
                with self.subTest(
                        reverse_name=reverse_name, field_name=field_name):
                    response = self.authorized_client.get(reverse_name)
                    form_field = response.context.get(
                        'form'
                    ).fields.get(field_name)
                    self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        resp_1 = response.content
        post_del = Post.objects.get(id=1)
        post_del.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        resp_2 = response_2.content
        self.assertTrue(resp_1 == resp_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        resp_3 = response_3.content
        self.assertTrue(resp_2 != resp_3)
