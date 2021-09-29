from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст для поста',
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(
            Post.objects.latest('pub_date').text, form_data['text']
        )
        self.assertEqual(
            Post.objects.latest('pub_date').author, self.user
        )
        self.assertEqual(
            Post.objects.latest('pub_date').group.id, form_data['group']
        )

    def test_edit_post(self):
        """Валидная форма редактирования записи в Post"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост больше 15 символов',
            group=self.group,
        )
        post_id = post.id
        form_data = {
            'text': 'Изменённый текст',
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(post_id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(post_id,))
        )
        self.assertEqual(Post.objects.get(id=post_id).text, form_data['text'])
