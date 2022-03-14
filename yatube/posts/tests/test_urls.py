from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост больше 15 символов',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_404_page_status_code(self):
        """Проверка вызова ошибки 404 при вызове несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_url_exists_at_desired_location(self):
        """По указанному URL-адресу открывается страница"""
        url_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user}),
            reverse('posts:post_detail',
                    args=(self.post.id,))
        ]
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_url_redirect_anonymous(self):
        """По указанному URL-адресу происходит перенаправление на другой URL"""
        url_names = {
            reverse('posts:post_create'):
            reverse('users:login') + '?next=' + reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post.id,)):
            reverse('users:login') + '?next='
            + reverse('posts:post_edit', args=(self.post.id,)),
            reverse('posts:follow_index'):
            reverse('users:login') + '?next=' + reverse('posts:follow_index'),
            reverse('posts:profile_follow', args=(self.user.username,)):
            reverse('users:login') + '?next='
            + reverse('posts:profile_follow', args=(self.user.username,)),
            reverse('posts:profile_unfollow', args=(self.user.username,)):
            reverse('users:login') + '?next='
            + reverse('posts:profile_unfollow', args=(self.user.username,)),
            reverse('posts:add_comment', args=(self.post.id,)):
            reverse('users:login') + '?next='
            + reverse('posts:add_comment', args=(self.post.id,)),
        }
        for adress, readres in url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, readres)

    def test_url_exists_at_desired_location_for_authorized(self):
        """По указанному URL-адресу открывается страница для авторизованных."""
        url_names = {
            reverse('posts:post_create'),
            reverse('posts:follow_index'),
        }
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_url_redirect_not_author(self):
        """По указанному URL-адресу происходит перенаправление на другой URL"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(self.post.id,)), follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,)))

    def test_url_exists_at_desired_location_for_author(self):
        """По указанному URL-адресу открывается страница для автора."""
        response = self.author_client.get(
            reverse('posts:post_edit', args=(self.post.id,)))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_for_url_app(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
            reverse('posts:post_detail', args=(self.post.id,)):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', args=(self.post.id,)):
            'posts/create_post.html',
            reverse('posts:follow_index'):
            'posts/follow.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)
