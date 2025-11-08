"""
Unit tests for LibraryUser model.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from users.models import LibraryUser


@pytest.mark.django_db
@pytest.mark.unit
class TestLibraryUserModel:
    """Test suite for LibraryUser model."""

    def test_create_user_success(self):
        """Test creating a user with valid data."""
        user = LibraryUser.objects.create(
            full_name='Test User',
            email='test@test.com',
            phone='11999999999',
            address='Test Street, 123',
            registration_number='TEST001',
            is_active=True
        )
        assert user.id is not None
        assert user.full_name == 'Test User'
        assert user.email == 'test@test.com'
        assert user.registration_number == 'TEST001'
        assert user.is_active is True

    def test_user_str_representation(self):
        """Test user string representation."""
        user = LibraryUser.objects.create(
            full_name='João Silva',
            email='joao@test.com',
            registration_number='2024001',
            is_active=True
        )
        assert str(user) == 'João Silva (2024001)'

    def test_can_borrow_when_active(self, sample_library_user):
        """Test can_borrow returns True when user is active."""
        assert sample_library_user.is_active is True
        assert sample_library_user.can_borrow() is True

    def test_cannot_borrow_when_inactive(self, inactive_library_user):
        """Test can_borrow returns False when user is inactive."""
        assert inactive_library_user.is_active is False
        assert inactive_library_user.can_borrow() is False

    def test_email_must_be_unique(self, sample_library_user):
        """Test email must be unique."""
        with pytest.raises(IntegrityError):
            LibraryUser.objects.create(
                full_name='Different User',
                email=sample_library_user.email,  # Duplicate email
                registration_number='DIFF001',
                is_active=True
            )

    def test_registration_number_must_be_unique(self, sample_library_user):
        """Test registration number must be unique."""
        with pytest.raises(IntegrityError):
            LibraryUser.objects.create(
                full_name='Different User',
                email='different@test.com',
                registration_number=sample_library_user.registration_number,  # Duplicate
                is_active=True
            )

    def test_create_user_with_minimal_fields(self):
        """Test creating user with only required fields."""
        user = LibraryUser.objects.create(
            full_name='Minimal User',
            email='minimal@test.com',
            registration_number='MIN001',
        )
        assert user.id is not None
        assert user.phone == ''
        assert user.address == ''
        assert user.is_active is True  # Default value

    def test_phone_is_optional(self):
        """Test phone field is optional."""
        user = LibraryUser.objects.create(
            full_name='No Phone User',
            email='nophone@test.com',
            registration_number='NP001',
        )
        assert user.phone == ''

    def test_address_is_optional(self):
        """Test address field is optional."""
        user = LibraryUser.objects.create(
            full_name='No Address User',
            email='noaddress@test.com',
            registration_number='NA001',
        )
        assert user.address == ''

    def test_is_active_defaults_to_true(self):
        """Test is_active defaults to True."""
        user = LibraryUser.objects.create(
            full_name='Default Active User',
            email='default@test.com',
            registration_number='DA001',
        )
        assert user.is_active is True

    def test_user_ordering(self):
        """Test users are ordered by full_name by default."""
        LibraryUser.objects.create(
            full_name='Zebra User',
            email='zebra@test.com',
            registration_number='Z001',
        )
        LibraryUser.objects.create(
            full_name='Alpha User',
            email='alpha@test.com',
            registration_number='A001',
        )

        users = list(LibraryUser.objects.all())
        assert users[0].full_name == 'Alpha User'
        assert users[1].full_name == 'Zebra User'

    def test_created_at_is_set_automatically(self):
        """Test created_at timestamp is set automatically."""
        user = LibraryUser.objects.create(
            full_name='Timestamp User',
            email='timestamp@test.com',
            registration_number='TS001',
        )
        assert user.created_at is not None

    def test_updated_at_is_updated_on_save(self):
        """Test updated_at timestamp is updated on save."""
        user = LibraryUser.objects.create(
            full_name='Update Test',
            email='update@test.com',
            registration_number='UP001',
        )
        original_updated = user.updated_at

        user.full_name = 'Updated Name'
        user.save()
        user.refresh_from_db()

        assert user.updated_at > original_updated

    def test_email_validation(self):
        """Test email field validates format."""
        with pytest.raises(ValidationError):
            user = LibraryUser(
                full_name='Invalid Email User',
                email='not_an_email',
                registration_number='IE001',
            )
            user.full_clean()

    def test_full_name_max_length(self):
        """Test full_name has max length constraint."""
        with pytest.raises(Exception):
            LibraryUser.objects.create(
                full_name='A' * 300,  # Exceeds max_length
                email='long@test.com',
                registration_number='LONG001',
            )

    def test_registration_number_max_length(self):
        """Test registration_number has max length constraint."""
        with pytest.raises(Exception):
            LibraryUser.objects.create(
                full_name='Test User',
                email='regnum@test.com',
                registration_number='A' * 100,  # Exceeds max_length
            )

    def test_phone_max_length(self):
        """Test phone has max length constraint."""
        with pytest.raises(Exception):
            LibraryUser.objects.create(
                full_name='Test User',
                email='phone@test.com',
                registration_number='PH001',
                phone='1' * 30,  # Exceeds max_length
            )

    def test_user_can_be_deactivated(self, sample_library_user):
        """Test user can be deactivated."""
        assert sample_library_user.is_active is True
        assert sample_library_user.can_borrow() is True

        sample_library_user.is_active = False
        sample_library_user.save()
        sample_library_user.refresh_from_db()

        assert sample_library_user.is_active is False
        assert sample_library_user.can_borrow() is False

    def test_user_can_be_reactivated(self, inactive_library_user):
        """Test inactive user can be reactivated."""
        assert inactive_library_user.is_active is False

        inactive_library_user.is_active = True
        inactive_library_user.save()
        inactive_library_user.refresh_from_db()

        assert inactive_library_user.is_active is True
        assert inactive_library_user.can_borrow() is True
