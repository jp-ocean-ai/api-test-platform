import pytest
from rest_framework.test import APIClient

from projects.models import Project


@pytest.mark.django_db
def test_create_project():
    client = APIClient()
    response = client.post(
        '/api/projects/',
        {
            'name': 'Demo Project',
            'description': 'First API test project',
            'owner': 'ocean',
            'is_active': True,
        },
        format='json',
    )
    assert response.status_code == 201
    assert Project.objects.count() == 1
