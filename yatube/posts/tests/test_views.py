from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostsPagesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст описания',
            slug='test-slug'
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        self.post = Post.objects.get(text='Тестовый текст')

    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующие шаблоны"""
        print(f'{self.test_pages_uses_correct_templates.__doc__}')
        # Собираем в словарь пары reverse(name): "имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={'slug': 'test-slug'})):
                'posts/group_list.html',
            reverse('posts:profile', args=[self.user]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.pk]):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args=[self.post.pk]):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response, template,
                    f'не тот {reverse_name} для {template}')

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_group = first_object.group
        post_text = first_object.text
        self.assertEqual(response.status_code, 200,
                         'страница index не доступна')
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_text, self.post.text)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.pk]))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.user)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts = []
        cls.author = User.objects.create_user(username='dimdim')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст описания',
            slug='test-slug'
        )
        cls.guest_client = Client()
        for count in range(1, 14):
            cls.posts.append(
                Post.objects.create(
                    text=f'Пост № {count}',
                    author=cls.author,
                    group=cls.group
                ))

    def test_page_contains_ten_records(self):
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.author])
        ]
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(len(response.context['page_obj']), 10)
                # Проверка: количество постов на второй странице равно 3.
                response = self.guest_client.get((reverse_name) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
