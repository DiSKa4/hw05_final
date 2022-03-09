from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()
POST_FIRST_PAGE = 10
POST_SECOND_PAGE = 3
COUNT_POSTS = POST_FIRST_PAGE + POST_SECOND_PAGE


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.authorized_client = Client()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.bulk_create([
            Post(author=cls.user, text='Тестовый пост', group=cls.group)
            for _ in range(COUNT_POSTS)
        ])
        cls.paginator_urls = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user}/'
        ]

    def test_first_page_contains_ten_records(self):

        pages = (
            (1, POST_FIRST_PAGE),
            (2, POST_SECOND_PAGE)
        )
        for page, count in pages:
            for url in self.paginator_urls:
                with self.subTest(url=url):
                    response = self.client.get(url, {"page": page})
                    self.assertEqual(
                        len(response.context["page_obj"].object_list), count
                    )
