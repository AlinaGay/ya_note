from django.urls import reverse


def test_note_in_list_for_author(note, author_client):
    url = reverse('notes:list')
    response = author_client.get(url)
    object_list = response.context['object_list']
    assert note in object_list

