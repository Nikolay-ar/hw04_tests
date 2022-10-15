from ..forms import PostForm
from ..models import Post, Group
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа Тестировщиков',
            description='Тестовый текст описания',
            slug='test-slug'
        )
        # Создаем форму для проверки атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        self.post = Post.objects.get(text='Тестовый текст')

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 1',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response,
                             reverse('posts:profile', args=[self.user]))
        self.assertEqual(
            Post.objects.count(), posts_count + 1,
            'Число постов не увеличилось')
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            author=self.user,
        ).exists(),
            'Не создалась запись с заданным текстом')
        new_post = Post.objects.latest('id')
        self.assertEqual(new_post.text, form_data['text'],
                         'post_create не правильно сохраняет текст поста')
        self.assertEqual(new_post.group.pk, form_data['group'],
                         'post_create не правильно сохраняет группу поста')
        self.assertEqual(new_post.author, self.user,
                         'post_create не правильно сохраняет автора поста')

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Тестовый текст 1',
            'group': self.group.pk }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id]))
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            author=self.user,
            id=self.post.id
        ).exists(),
            'Не сохранилась запись с заданным текстом в нуном посте')
        edit_post = Post.objects.get(id=self.post.id)
        self.assertEqual(edit_post.text, form_data['text'],
                         'post_create не правильно сохраняет текст поста')
        self.assertEqual(edit_post.group.pk, form_data['group'],
                         'post_create не правильно сохраняет группу поста')
        self.assertEqual(edit_post.author, self.user,
                         'post_create не правильно сохраняет автора поста')
