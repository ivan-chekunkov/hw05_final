from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_tech_page(self):
        """По указанному URL-адресу открывается страница """
        url_names = [
            reverse('about:tech'),
            reverse('about:author')
        ]
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_correct_template_for_url_app(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('about:tech'): 'about/tech.html',
            reverse('about:author'): 'about/author.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
