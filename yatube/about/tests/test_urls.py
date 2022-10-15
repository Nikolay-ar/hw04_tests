from django.test import TestCase, Client


class AuthorTechPageURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /author/ и шаблона author.html."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/author.html')

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /tech/ и шаблона tech.html."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/tech.html')
