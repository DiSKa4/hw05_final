import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': "Author"
            }
        )
        )
        response = self.guest_client.post(
            reverse(
                'posts:post_create')
        )
        self.assertRedirects(response, '/auth/login/?next=%2Fcreate%2F')
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        new_group = Group.objects.create(
            title='new_group',
            slug='slug_new_group',
            description='Описание new_group'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новое Редактирование текста',
            'group': new_group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post.id
            }
        )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=form_data['author']
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_auth_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
            'author': self.user
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}),
                data=form_data,
                follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={
                'post_id': self.post.id
                }
        )
        )
        response_1 = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={
                    'post_id': self.post.id}))
        self.assertRedirects(
            response_1,
            '/auth/login/?next=%2Fposts%2F1%2Fcomment%2F'
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=form_data['author']
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_auth_follow(self):
        new_user = User.objects.create_user(username='new_user')
        self.authorized_client.force_login(new_user)
        Follow.objects.create(user=new_user, author=self.user)
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args=(self.user,))
        )
        self.assertRedirects(response, f'/profile/{self.user}/')
        self.assertEqual(Follow.objects.count(), 1)
        response_1 = self.authorized_client.post(
            reverse('posts:profile_unfollow', args=(self.user,))
        )
        self.assertRedirects(response_1, f'/profile/{self.user}/')
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_post(self):
        new_user = User.objects.create_user(username='new_user')
        self.authorized_client.force_login(new_user)
        self.follow = Follow.objects.create(user=new_user, author=self.user)
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        qs = Follow.objects.filter(user=self.user)
        self.assertTrue(response.context['page_obj'].object_list, qs)

    def test_follow_post_not_follow(self):
        new_user = User.objects.create_user(username='new_user')
        self.authorized_client.force_login(new_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        qs = Follow.objects.filter(user=self.user)
        self.assertFalse(response.context['page_obj'].object_list, qs)
