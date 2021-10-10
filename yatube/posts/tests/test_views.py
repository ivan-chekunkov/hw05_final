import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
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
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост больше 15 символов',
            group=self.group,
            image=uploaded,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:post_detail',
                    args=(self.post.id,)):
            'posts/post_detail.html',
            reverse('posts:post_edit',
                    args=(self.post.id,)):
            'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}):
            'posts/profile.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context_post(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.group, self.group)
            self.assertEqual(
                post.image, self.post.image
            )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_context_post(first_object)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.check_context_post(first_object)
        group_object = response.context['group']
        self.assertEqual(group_object.title, self.group.title)
        self.assertEqual(group_object.slug, self.group.slug)
        self.assertEqual(group_object.description, self.group.description)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        context = response.context['post']
        self.check_context_post(context)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        first_object = response.context['page_obj'][0]
        self.check_context_post(first_object)
        author = response.context['author']
        self.assertEqual(author, self.user)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с верным контекстом формы"""
        response = self.author_client.get(
            reverse('posts:post_edit', args=(self.post.id,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        context = response.context['post']
        self.check_context_post(context)
        self.assertEqual(response.context['is_edit'], True)

    def test_create_post_in_true_group(self):
        """При указании группы пост появиться только в нужной группе"""
        group = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': group.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(15):
            Post.objects.create(
                author=cls.user,
                text='№' + str(i) + ' Тестовый пост больше 15 символов',
                group=cls.group,
            )

    def test_paginator(self):
        url_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        ]
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(adress + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 5)


class CacheTests(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_cahce_index(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост больше 15 символов',
        )
        response = self.author_client.get(reverse('posts:index'))
        content_before_delete = response.content
        post.delete()
        response = self.author_client.get(reverse('posts:index'))
        content_after_delete = response.content
        self.assertEqual(content_after_delete, content_before_delete)
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        content_before_clear = response.content
        self.assertNotEqual(content_before_clear, content_before_delete)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='follower')
        cls.second_user = User.objects.create_user(username='following')

    def setUp(self):
        self.first_user_client = Client()
        self.second_user_client = Client()
        self.first_user_client.force_login(self.first_user)
        self.second_user_client.force_login(self.second_user)
        cache.clear()

    def test_follow(self):
        """Проверка подписки на автора"""
        count = Follow.objects.count()
        self.second_user_client.post(
            reverse('posts:profile_follow', args=(self.first_user.username,)))
        count_after = Follow.objects.count()
        latest_follow = Follow.objects.latest('id')
        self.assertEqual(count_after, count + 1)
        self.assertEqual(latest_follow.user, self.second_user)
        self.assertEqual(latest_follow.author, self.first_user)

    def test_unfollow(self):
        """Проверка отписки от автора"""
        Follow.objects.create(
            user=self.first_user,
            author=self.second_user
        )
        count = Follow.objects.count()
        self.first_user_client.post(
            reverse('posts:profile_unfollow',
                    args=(self.second_user.username,)))
        count_after = Follow.objects.count()
        self.assertEqual(count_after, count - 1)

    def test_follow_index_empty(self):
        """Правильное отображение follow_index пустого"""
        response = self.first_user_client.post(
            reverse('posts:follow_index'),
        )
        count = len(response.context['page_obj'])
        self.assertEqual(count, 0)

    def test_follow_index(self):
        """Правильное отображение follow_index"""
        Follow.objects.create(
            user=self.first_user,
            author=self.second_user
        )
        post = Post.objects.create(
            text="Тестовый пост №2",
            author=self.second_user
        )
        response = self.first_user_client.post(
            reverse('posts:follow_index'),
        )
        post_response = response.context['page_obj'][0]
        self.assertEqual(post_response, post)
