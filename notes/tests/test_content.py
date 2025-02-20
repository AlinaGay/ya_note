from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestAddPage(TestCase):

    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пользователь')
        cls.reader = User.objects.create(username='Читатель')
        

    def test_autorized_user_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пользователь')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='new',
            author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_note_in_list_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
 
