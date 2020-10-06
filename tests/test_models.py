from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase

from app.models import Author, Occurrence


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        user = User.objects.create(username='author')
        Author.objects.create(user=user)

    def test_author_has_username_field_from_user(self):
        author = Author.objects.get(user_id=1)
        self.assertEquals('author', author.user.username)


class OccurrenceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        management.call_command('flush', interactive=False)
        user = User.objects.create(username='author')
        author = Author.objects.create(user=user)
        point = 'POINT(0 0)'
        description = 'description'
        category = 'construction'
        Occurrence.objects.create(author=author, point=point, description=description, category=category)

    def test_default_status(self):
        occurrence = Occurrence.objects.get(id=1)
        self.assertEquals('to_validate', occurrence.status)
