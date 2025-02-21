from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    NOTE_TITLE = 'Заголовок другой'
    NOTE_TEXT = 'Текст другой'
    NOTE_SLUG = 'another_new'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Автор')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'author': cls.author
        }

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertAlmostEqual(note.author, self.author)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestSlugChecking(TestCase):

    NOTE_TITLE = 'Заголовок другой'
    NOTE_TEXT = 'Текст другой'
    NOTE_SLUG = 'another_new'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='new',
            author=cls.author
        )
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'author': cls.author
        }

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(TestCase):

    NOTE_TEXT = 'Текст'
    NEW_NOTE_TITLE = 'Заголовок другой'
    NEW_NOTE_TEXT = 'Текст другой'
    NEW_NOTE_SLUG = 'another_new'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='new',
            author=cls.author
        )

        cls.notes_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
            'author': cls.author
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
