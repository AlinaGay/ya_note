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

    def test_autorized_user_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пользователь')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'new-{index}',
                author=cls.author
            )
            for index in range(settings.NOTES_COUNT_ON_LIST_PAGE)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, settings.NOTES_COUNT_ON_LIST_PAGE)
