"""
Unit tests for UserRepository.
"""
import pytest

from users.models import LibraryUser
from users.repositories.user_repository import UserRepository


@pytest.mark.django_db
@pytest.mark.unit
class TestUserRepository:
    """Test suite for UserRepository."""

    def test_get_all_returns_all_users(self, multiple_library_users):
        """Test get_all returns all users in the database."""
        users = UserRepository.get_all()
        assert users.count() == 3
        # Check they're ordered by full_name (default ordering)
        names = [user.full_name for user in users]
        assert names == sorted(names)

    def test_get_all_returns_empty_queryset_when_no_users(self):
        """Test get_all returns empty queryset when no users exist."""
        users = UserRepository.get_all()
        assert users.count() == 0

    def test_get_by_id_returns_user_when_exists(self, sample_library_user):
        """Test get_by_id returns user when it exists."""
        user = UserRepository.get_by_id(sample_library_user.id)
        assert user is not None
        assert user.id == sample_library_user.id
        assert user.full_name == sample_library_user.full_name

    def test_get_by_id_returns_none_when_not_exists(self):
        """Test get_by_id returns None when user doesn't exist."""
        user = UserRepository.get_by_id(99999)
        assert user is None

    def test_get_by_registration_number_returns_user_when_exists(self, sample_library_user):
        """Test get_by_registration_number returns user when it exists."""
        user = UserRepository.get_by_registration_number(sample_library_user.registration_number)
        assert user is not None
        assert user.registration_number == sample_library_user.registration_number
        assert user.full_name == sample_library_user.full_name

    def test_get_by_registration_number_returns_none_when_not_exists(self):
        """Test get_by_registration_number returns None when doesn't exist."""
        user = UserRepository.get_by_registration_number('NONEXISTENT')
        assert user is None

    def test_get_by_email_returns_user_when_exists(self, sample_library_user):
        """Test get_by_email returns user when it exists."""
        user = UserRepository.get_by_email(sample_library_user.email)
        assert user is not None
        assert user.email == sample_library_user.email
        assert user.full_name == sample_library_user.full_name

    def test_get_by_email_returns_none_when_not_exists(self):
        """Test get_by_email returns None when doesn't exist."""
        user = UserRepository.get_by_email('nonexistent@test.com')
        assert user is None

    def test_get_active_users_returns_only_active(self, sample_library_user, inactive_library_user):
        """Test get_active_users returns only active users."""
        users = UserRepository.get_active_users()
        assert users.count() == 1
        assert users.first().id == sample_library_user.id
        assert users.first().is_active is True

    def test_get_active_users_returns_empty_when_none_active(self, inactive_library_user):
        """Test get_active_users returns empty when no active users."""
        users = UserRepository.get_active_users()
        assert users.count() == 0

    def test_get_active_users_with_multiple_active(self, multiple_library_users):
        """Test get_active_users returns all active users."""
        users = UserRepository.get_active_users()
        assert users.count() == 2  # Two active users in fixture
        for user in users:
            assert user.is_active is True

    def test_search_by_name_finds_exact_match(self, sample_library_user):
        """Test search_by_name finds exact name match."""
        users = UserRepository.search_by_name('João Silva')
        assert users.count() == 1
        assert users.first().full_name == 'João Silva'

    def test_search_by_name_finds_partial_match(self, sample_library_user):
        """Test search_by_name finds partial matches."""
        users = UserRepository.search_by_name('João')
        assert users.count() == 1
        assert 'João' in users.first().full_name

    def test_search_by_name_is_case_insensitive(self, sample_library_user):
        """Test search_by_name is case insensitive."""
        users = UserRepository.search_by_name('joão silva')
        assert users.count() == 1
        users = UserRepository.search_by_name('JOÃO SILVA')
        assert users.count() == 1

    def test_search_by_name_returns_empty_when_no_match(self):
        """Test search_by_name returns empty queryset when no match."""
        users = UserRepository.search_by_name('Nonexistent User')
        assert users.count() == 0

    def test_search_by_name_returns_multiple_matches(self):
        """Test search_by_name returns multiple matching users."""
        LibraryUser.objects.create(
            full_name='João Silva',
            email='joao1@test.com',
            registration_number='J001',
        )
        LibraryUser.objects.create(
            full_name='João Santos',
            email='joao2@test.com',
            registration_number='J002',
        )

        users = UserRepository.search_by_name('João')
        assert users.count() == 2

    def test_create_user_success(self):
        """Test create successfully creates a new user."""
        data = {
            'full_name': 'New User',
            'email': 'newuser@test.com',
            'phone': '11988887777',
            'address': 'New Street, 456',
            'registration_number': 'NEW001',
            'is_active': True
        }
        user = UserRepository.create(data)
        assert user.id is not None
        assert user.full_name == 'New User'
        assert user.email == 'newuser@test.com'
        assert user.registration_number == 'NEW001'

        # Verify it was saved to database
        saved_user = LibraryUser.objects.get(id=user.id)
        assert saved_user.full_name == 'New User'

    def test_create_user_with_minimal_data(self):
        """Test create with only required fields."""
        data = {
            'full_name': 'Minimal User',
            'email': 'minimal@test.com',
            'registration_number': 'MIN001',
        }
        user = UserRepository.create(data)
        assert user.id is not None
        assert user.full_name == 'Minimal User'
        assert user.is_active is True  # Default value

    def test_update_user_success(self, sample_library_user):
        """Test update successfully updates a user."""
        data = {
            'full_name': 'Updated Name',
            'phone': '11900000000'
        }
        updated_user = UserRepository.update(sample_library_user, data)
        assert updated_user.full_name == 'Updated Name'
        assert updated_user.phone == '11900000000'
        assert updated_user.email == sample_library_user.email  # Unchanged field

        # Verify it was saved to database
        sample_library_user.refresh_from_db()
        assert sample_library_user.full_name == 'Updated Name'
        assert sample_library_user.phone == '11900000000'

    def test_update_user_partial_update(self, sample_library_user):
        """Test update with partial data updates only specified fields."""
        original_email = sample_library_user.email
        data = {'full_name': 'New Name Only'}
        UserRepository.update(sample_library_user, data)

        sample_library_user.refresh_from_db()
        assert sample_library_user.full_name == 'New Name Only'
        assert sample_library_user.email == original_email

    def test_update_user_activation_status(self, sample_library_user):
        """Test update can change activation status."""
        assert sample_library_user.is_active is True

        data = {'is_active': False}
        UserRepository.update(sample_library_user, data)

        sample_library_user.refresh_from_db()
        assert sample_library_user.is_active is False

    def test_delete_user_success(self, sample_library_user):
        """Test delete successfully removes a user."""
        user_id = sample_library_user.id
        UserRepository.delete(sample_library_user)

        # Verify it was deleted from database
        assert LibraryUser.objects.filter(id=user_id).count() == 0

    def test_repository_operations_are_transactional(self):
        """Test repository operations maintain data integrity."""
        # Create a user
        user = UserRepository.create({
            'full_name': 'Transaction Test',
            'email': 'transaction@test.com',
            'registration_number': 'TR001',
        })

        # Update it
        UserRepository.update(user, {'full_name': 'Updated Transaction Test'})
        user.refresh_from_db()
        assert user.full_name == 'Updated Transaction Test'

        # Delete it
        UserRepository.delete(user)
        assert LibraryUser.objects.filter(email='transaction@test.com').count() == 0
