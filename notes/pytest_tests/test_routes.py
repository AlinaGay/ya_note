from http import HTTPStatus

from django.urls import reverse


def test_home_availbility_for_anonymous_user(client):
    url = reverse('notes:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
