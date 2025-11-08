"""
Integration tests for Users API endpoints.
"""
import io
import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from users.models import LibraryUser


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetList:
    """Test suite for listing users."""

    def test_list_users_returns_all_users(self, authenticated_client, multiple_library_users):
        """Test GET /api/users/ returns all users."""
        response = authenticated_client.get('/api/users/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_list_users_returns_empty_when_no_users(self, authenticated_client):
        """Test GET /api/users/ returns empty list when no users."""
        response = authenticated_client.get('/api/users/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_users_uses_list_serializer(self, authenticated_client, sample_library_user):
        """Test list endpoint uses LibraryUserListSerializer."""
        response = authenticated_client.get('/api/users/')

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data[0]

        # LibraryUserListSerializer fields
        assert 'id' in user_data
        assert 'full_name' in user_data
        assert 'registration_number' in user_data
        assert 'email' in user_data
        assert 'is_active' in user_data
        assert 'can_borrow' in user_data

        # Fields not in LibraryUserListSerializer
        assert 'phone' not in user_data
        assert 'address' not in user_data
        assert 'created_at' not in user_data


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetRetrieve:
    """Test suite for retrieving a single user."""

    def test_retrieve_user_success(self, authenticated_client, sample_library_user):
        """Test GET /api/users/{id}/ returns user details."""
        response = authenticated_client.get(f'/api/users/{sample_library_user.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_library_user.id
        assert response.data['full_name'] == sample_library_user.full_name
        assert response.data['email'] == sample_library_user.email

    def test_retrieve_user_not_found(self, authenticated_client):
        """Test GET /api/users/{id}/ returns 404 for non-existent user."""
        response = authenticated_client.get('/api/users/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_user_uses_full_serializer(self, authenticated_client, sample_library_user):
        """Test retrieve endpoint uses LibraryUserSerializer with all fields."""
        response = authenticated_client.get(f'/api/users/{sample_library_user.id}/')

        assert response.status_code == status.HTTP_200_OK
        # Should have all fields from LibraryUserSerializer
        assert 'phone' in response.data
        assert 'address' in response.data
        assert 'created_at' in response.data
        assert 'updated_at' in response.data


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetCreate:
    """Test suite for creating users."""

    def test_create_user_success(self, authenticated_client):
        """Test POST /api/users/ creates a new user."""
        data = {
            'full_name': 'New User',
            'email': 'newuser@test.com',
            'phone': '11999999999',
            'address': 'New Street, 123',
            'registration_number': 'NEW001',
            'is_active': True
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['full_name'] == 'New User'
        assert response.data['email'] == 'newuser@test.com'

        # Verify user was created in database
        assert LibraryUser.objects.filter(registration_number='NEW001').exists()

    def test_create_user_with_minimal_data(self, authenticated_client):
        """Test POST /api/users/ with only required fields."""
        data = {
            'full_name': 'Minimal User',
            'email': 'minimal@test.com',
            'registration_number': 'MIN001',
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_active'] is True  # Default value

    def test_create_user_duplicate_registration_number(self, authenticated_client, sample_library_user):
        """Test POST /api/users/ with duplicate registration number returns 400."""
        data = {
            'full_name': 'Duplicate User',
            'email': 'duplicate@test.com',
            'registration_number': sample_library_user.registration_number,
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'registration_number' in response.data

    def test_create_user_duplicate_email(self, authenticated_client, sample_library_user):
        """Test POST /api/users/ with duplicate email returns 400."""
        data = {
            'full_name': 'Duplicate User',
            'email': sample_library_user.email,
            'registration_number': 'DUP001',
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_create_user_invalid_email(self, authenticated_client):
        """Test POST /api/users/ with invalid email returns 400."""
        data = {
            'full_name': 'Invalid Email User',
            'email': 'not_an_email',
            'registration_number': 'INV001',
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_create_user_missing_required_fields(self, authenticated_client):
        """Test POST /api/users/ with missing required fields returns 400."""
        data = {
            'full_name': 'Incomplete User',
            # Missing email and registration_number
        }
        response = authenticated_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_unauthenticated(self, api_client):
        """Test POST /api/users/ without authentication returns 401."""
        data = {
            'full_name': 'New User',
            'email': 'newuser@test.com',
            'registration_number': 'NEW001',
        }
        response = api_client.post('/api/users/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetUpdate:
    """Test suite for updating users."""

    def test_update_user_success(self, authenticated_client, sample_library_user):
        """Test PUT /api/users/{id}/ updates a user."""
        data = {
            'full_name': 'Updated Name',
            'email': sample_library_user.email,  # Must be included
            'phone': '11900000000',
            'address': 'Updated Address',
            'registration_number': sample_library_user.registration_number,
            'is_active': True
        }
        response = authenticated_client.put(f'/api/users/{sample_library_user.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Updated Name'
        assert response.data['phone'] == '11900000000'

        # Verify database was updated
        sample_library_user.refresh_from_db()
        assert sample_library_user.full_name == 'Updated Name'

    def test_partial_update_user_success(self, authenticated_client, sample_library_user):
        """Test PATCH /api/users/{id}/ partially updates a user."""
        data = {'full_name': 'Partially Updated Name'}
        response = authenticated_client.patch(f'/api/users/{sample_library_user.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Partially Updated Name'
        # Other fields should remain unchanged
        assert response.data['email'] == sample_library_user.email

    def test_update_user_activation_status(self, authenticated_client, sample_library_user):
        """Test updating user activation status."""
        data = {'is_active': False}
        response = authenticated_client.patch(f'/api/users/{sample_library_user.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is False

        sample_library_user.refresh_from_db()
        assert sample_library_user.is_active is False

    def test_update_user_not_found(self, authenticated_client):
        """Test PUT /api/users/{id}/ returns 404 for non-existent user."""
        data = {
            'full_name': 'Updated Name',
            'email': 'updated@test.com',
            'registration_number': 'UPD001',
        }
        response = authenticated_client.put('/api/users/99999/', data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetDelete:
    """Test suite for deleting users."""

    def test_delete_user_success(self, authenticated_client, sample_library_user):
        """Test DELETE /api/users/{id}/ deletes a user."""
        user_id = sample_library_user.id
        response = authenticated_client.delete(f'/api/users/{user_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify user was deleted
        assert not LibraryUser.objects.filter(id=user_id).exists()

    def test_delete_user_not_found(self, authenticated_client):
        """Test DELETE /api/users/{id}/ returns 404 for non-existent user."""
        response = authenticated_client.delete('/api/users/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetActive:
    """Test suite for active users endpoint."""

    def test_active_users_returns_only_active(self, authenticated_client, sample_library_user, inactive_library_user):
        """Test GET /api/users/active/ returns only active users."""
        response = authenticated_client.get('/api/users/active/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == sample_library_user.id
        assert response.data[0]['is_active'] is True

    def test_active_users_returns_empty_when_none_active(self, authenticated_client, inactive_library_user):
        """Test GET /api/users/active/ returns empty when no active users."""
        response = authenticated_client.get('/api/users/active/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_active_users_uses_list_serializer(self, authenticated_client, sample_library_user):
        """Test active endpoint uses LibraryUserListSerializer."""
        response = authenticated_client.get('/api/users/active/')

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data[0]
        assert 'can_borrow' in user_data


@pytest.mark.django_db
@pytest.mark.integration
class TestLibraryUserViewSetBulkUpload:
    """Test suite for bulk upload endpoint."""

    def test_bulk_upload_txt_success(self, authenticated_client):
        """Test POST /api/users/bulk_upload/ with valid TXT file."""
        content = """full_name|email|phone|address|registration_number|is_active
João Silva|joao@test.com|11999999999|Rua A, 123|REG001|True
Maria Santos|maria@test.com|11988888888|Rua B, 456|REG002|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2
        assert 'Successfully imported' in response.data['message']

        # Verify users were created
        assert LibraryUser.objects.count() == 2

    def test_bulk_upload_excel_success(self, authenticated_client):
        """Test POST /api/users/bulk_upload/ with valid Excel file."""
        data_rows = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                'phone': '11999999999',
                'address': 'Rua A, 123',
                'registration_number': 'REG001',
                'is_active': True
            },
            {
                'full_name': 'Maria Santos',
                'email': 'maria@test.com',
                'phone': '11988888888',
                'address': 'Rua B, 456',
                'registration_number': 'REG002',
                'is_active': True
            }
        ]

        df = pd.DataFrame(data_rows)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        file = SimpleUploadedFile("users.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {
            'file': file,
            'file_type': 'excel'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2
        assert LibraryUser.objects.count() == 2

    def test_bulk_upload_invalid_file_type(self, authenticated_client):
        """Test POST /api/users/bulk_upload/ with invalid file type."""
        file = SimpleUploadedFile("users.txt", b"content", content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'invalid'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_upload_wrong_file_extension(self, authenticated_client):
        """Test POST /api/users/bulk_upload/ with wrong file extension."""
        file = SimpleUploadedFile("users.pdf", b"content", content_type="application/pdf")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_upload_invalid_content(self, authenticated_client):
        """Test POST /api/users/bulk_upload/ with invalid content."""
        content = """wrong|header
data|here"""
        file = SimpleUploadedFile("users.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['created'] == 0

    def test_bulk_upload_partial_success(self, authenticated_client, sample_library_user):
        """Test bulk upload with some valid and some invalid rows."""
        content = f"""full_name|email|phone|address|registration_number|is_active
New User|newuser@test.com|11999999999|Street 1|NEW001|True
Duplicate|dup@test.com|11988888888|Street 2|{sample_library_user.registration_number}|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 1
        assert len(response.data['errors']) > 0

    def test_bulk_upload_requires_authentication(self, api_client):
        """Test POST /api/users/bulk_upload/ requires authentication."""
        file = SimpleUploadedFile("users.txt", b"content", content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = api_client.post('/api/users/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
