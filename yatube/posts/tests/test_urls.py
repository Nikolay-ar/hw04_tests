# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsURLTestCase(TestCase):
    """Тестируем URLs"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Для класса PostsURLTestCase создадим пользователя модели User
        cls.user = User.objects.create_user(username='TestUser')
        cls.user1 = User.objects.create_user(username='TestUser1')
        Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст описания',
            slug='test-slug'
        )
        # Создадим запись в БД для проверки доступности адреса /posts/post-id/
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1.force_login(self.user1)

    def test_urls_use_correct_templates(self):
        """URL адреса используют соответствующие шаблоны
        и доступны любому пользователю"""
        print(f'{self.test_urls_use_correct_templates.__doc__}')
        expected_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for url, template in expected_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 200, 'страница не доступна')
                self.assertTemplateUsed(response, template, 'не тот template')

    def test_urls_use_correct_templates_and_redirect(self):
        """URL адреса используют соответствующие шаблоны и доступны
        авторизованному пользователю, а не авторизованному - редирект"""
        expected_templates = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in expected_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, 302, 'не выполняется редирект')
                response = self.authorized_client.get('/create/')
                self.assertEqual(
                    response.status_code, 200, 'страница не доступна')
                self.assertTemplateUsed(response, template, 'не тот template')

    def test_not_the_author_urls_use_redirect(self):
        """URL адрес не доступен авторизованному пользователю, не автору"""
        response = self.authorized_client1.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(
            response.status_code, 302, 'не выполняется редирект')
