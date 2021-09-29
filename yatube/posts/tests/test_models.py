from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост больше 15 символов',
        )

    def test_verbose_name_model_post(self):
        """verbose_name модели Post совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_model_post(self):
        """help_text модели Post совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_models_post_have_correct_object_names(self):
        """__str__ модели Post совпадает с ожидаемым."""
        post = self.post
        text_15 = self.post.text[:15]
        self.assertEqual(str(post), text_15)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_verbose_name_model_group(self):
        """verbose_name модели Group совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Человекочитаемый ID',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_model_group(self):
        """help_text модели Group совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Введите название группы',
            'description': 'Опишите название группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_models_group_have_correct_object_names(self):
        """__str__ модели Group совпадает с ожидаемым."""
        group = self.group
        group_test_title = self.group.title
        self.assertEqual(str(group), group_test_title)
