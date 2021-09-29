from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):

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
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

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
