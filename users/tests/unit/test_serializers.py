"""
Unit tests for LibraryUser serializers.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from users.serializers import (
    LibraryUserSerializer,
    LibraryUserListSerializer,
    LibraryUserBulkUploadSerializer,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestLibraryUserSerializer:
    """Test suite for LibraryUserSerializer."""

    def test_serialize_user(self, sample_library_user):
        """Test serializing a user instance."""
        serializer = LibraryUserSerializer(sample_library_user)
        data = serializer.data

        assert data['id'] == sample_library_user.id
        assert data['full_name'] == sample_library_user.full_name
        assert data['email'] == sample_library_user.email
        assert data['phone'] == sample_library_user.phone
        assert data['registration_number'] == sample_library_user.registration_number
        assert data['is_active'] == sample_library_user.is_active

    def test_deserialize_valid_user_data(self):
        """Test deserializing valid user data."""
        data = {
            'full_name': 'Test User',
            'email': 'test@test.com',
            'phone': '11999999999',
            'address': 'Test Street, 123',
            'registration_number': 'TEST001',
            'is_active': True
        }
        serializer = LibraryUserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.full_name == 'Test User'
        assert user.email == 'test@test.com'

    def test_registration_number_must_be_unique_on_create(self, sample_library_user):
        """Test registration number validation rejects duplicates on create."""
        data = {
            'full_name': 'Different User',
            'email': 'different@test.com',
            'registration_number': sample_library_user.registration_number,
            'is_active': True
        }
        serializer = LibraryUserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'registration_number' in serializer.errors
        assert 'already exists' in str(serializer.errors['registration_number'])

    def test_registration_number_validation_on_update(self, sample_library_user):
        """Test registration number validation on update."""
        # Create another user
        other_user = LibraryUser.objects.create(
            full_name='Other User',
            email='other@test.com',
            registration_number='OTHER001',
            is_active=True
        )

        # Try to update sample_library_user with other_user's registration number
        data = {'registration_number': other_user.registration_number}
        serializer = LibraryUserSerializer(sample_library_user, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'registration_number' in serializer.errors

    def test_registration_number_can_stay_same_on_update(self, sample_library_user):
        """Test user can keep same registration number when updating other fields."""
        data = {
            'full_name': 'Updated Name',
            'registration_number': sample_library_user.registration_number  # Same number
        }
        serializer = LibraryUserSerializer(sample_library_user, data=data, partial=True)
        assert serializer.is_valid()

    def test_email_validation(self):
        """Test email field validates format."""
        data = {
            'full_name': 'Test User',
            'email': 'not_an_email',
            'registration_number': 'TEST001',
        }
        serializer = LibraryUserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_create_user_with_minimal_data(self):
        """Test creating user with only required fields."""
        data = {
            'full_name': 'Minimal User',
            'email': 'minimal@test.com',
            'registration_number': 'MIN001',
        }
        serializer = LibraryUserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.full_name == 'Minimal User'
        assert user.is_active is True  # Default value

    def test_is_active_defaults_to_true(self):
        """Test is_active defaults to True if not provided."""
        data = {
            'full_name': 'Test User',
            'email': 'test@test.com',
            'registration_number': 'TEST001',
        }
        serializer = LibraryUserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.is_active is True

    def test_read_only_fields_cannot_be_set(self):
        """Test that read-only fields cannot be modified."""
        from datetime import datetime
        data = {
            'full_name': 'Test User',
            'email': 'test@test.com',
            'registration_number': 'TEST001',
            'id': 9999,  # Should be read-only
            'created_at': datetime.now(),  # Should be read-only
        }
        serializer = LibraryUserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.id != 9999  # ID should be auto-generated

    def test_update_user_success(self, sample_library_user):
        """Test updating user fields."""
        data = {
            'full_name': 'Updated Name',
            'phone': '11988888888'
        }
        serializer = LibraryUserSerializer(sample_library_user, data=data, partial=True)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.full_name == 'Updated Name'
        assert user.phone == '11988888888'


@pytest.mark.django_db
@pytest.mark.unit
class TestLibraryUserListSerializer:
    """Test suite for LibraryUserListSerializer."""

    def test_serialize_user_list(self, sample_library_user):
        """Test serializing a user for list view."""
        serializer = LibraryUserListSerializer(sample_library_user)
        data = serializer.data

        assert 'id' in data
        assert 'full_name' in data
        assert 'registration_number' in data
        assert 'email' in data
        assert 'is_active' in data
        assert 'can_borrow' in data

        # Should not include detailed fields
        assert 'phone' not in data
        assert 'address' not in data
        assert 'created_at' not in data
        assert 'updated_at' not in data

    def test_can_borrow_field_reflects_status(self, sample_library_user, inactive_library_user):
        """Test can_borrow field shows correct status."""
        # Active user
        serializer = LibraryUserListSerializer(sample_library_user)
        assert serializer.data['can_borrow'] is True

        # Inactive user
        serializer = LibraryUserListSerializer(inactive_library_user)
        assert serializer.data['can_borrow'] is False

    def test_serialize_multiple_users(self, multiple_library_users):
        """Test serializing multiple users."""
        serializer = LibraryUserListSerializer(multiple_library_users, many=True)
        data = serializer.data

        assert len(data) == 3
        for user_data in data:
            assert 'full_name' in user_data
            assert 'registration_number' in user_data
            assert 'can_borrow' in user_data


@pytest.mark.unit
class TestLibraryUserBulkUploadSerializer:
    """Test suite for LibraryUserBulkUploadSerializer."""

    def test_valid_txt_file(self):
        """Test validation accepts valid TXT file."""
        file_content = b"Name|Email|Registration\nTest|test@test.com|TEST001"
        file = SimpleUploadedFile("users.txt", file_content, content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_valid_excel_file(self):
        """Test validation accepts valid Excel file."""
        file = SimpleUploadedFile("users.xlsx", b"fake excel content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_txt_file_type_rejects_non_txt_extension(self):
        """Test TXT file type rejects non-.txt files."""
        file = SimpleUploadedFile("users.xlsx", b"content", content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_excel_file_type_rejects_non_excel_extension(self):
        """Test Excel file type rejects non-Excel files."""
        file = SimpleUploadedFile("users.txt", b"content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_file_size_limit_10mb(self):
        """Test file size cannot exceed 10MB."""
        # Create a file larger than 10MB
        large_content = b"x" * (10485761)  # 10MB + 1 byte
        file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_file_type_choices(self):
        """Test file_type field only accepts 'txt' or 'excel'."""
        file = SimpleUploadedFile("users.txt", b"content", content_type="text/plain")

        # Invalid file_type
        data = {'file': file, 'file_type': 'pdf'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file_type' in serializer.errors

    def test_xlsx_extension_accepted(self):
        """Test .xlsx extension is accepted for Excel files."""
        file = SimpleUploadedFile("users.xlsx", b"content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_xls_extension_accepted(self):
        """Test .xls extension is accepted for Excel files."""
        file = SimpleUploadedFile("users.xls", b"content", content_type="application/vnd.ms-excel")

        data = {'file': file, 'file_type': 'excel'}
        serializer = LibraryUserBulkUploadSerializer(data=data)
        assert serializer.is_valid()


# Import LibraryUser to fix undefined reference
from users.models import LibraryUser
