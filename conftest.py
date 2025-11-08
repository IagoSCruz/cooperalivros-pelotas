"""
Shared test fixtures for the entire test suite.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book
from users.models import LibraryUser
from loans.models import Loan


@pytest.fixture
def api_client():
    """Returns an API client for testing endpoints."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Returns an authenticated API client with admin privileges."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_user(db):
    """Creates an admin user for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )


@pytest.fixture
def sample_book(db):
    """Creates a sample book for testing."""
    return Book.objects.create(
        title='Clean Code',
        author='Robert C. Martin',
        isbn='978-0132350884',
        publisher='Prentice Hall',
        publication_year=2008,
        category='Software Engineering',
        quantity=5,
        available_quantity=5
    )


@pytest.fixture
def sample_book_with_no_copies(db):
    """Creates a book with zero copies available."""
    return Book.objects.create(
        title='Out of Stock Book',
        author='Test Author',
        isbn='978-1234567890',
        publisher='Test Publisher',
        publication_year=2020,
        category='Fiction',
        quantity=3,
        available_quantity=0
    )


@pytest.fixture
def multiple_books(db):
    """Creates multiple books for testing list operations."""
    books = [
        Book.objects.create(
            title='The Pragmatic Programmer',
            author='Andrew Hunt',
            isbn='978-0201616224',
            publisher='Addison-Wesley',
            publication_year=1999,
            category='Software Engineering',
            quantity=3,
            available_quantity=3
        ),
        Book.objects.create(
            title='Design Patterns',
            author='Gang of Four',
            isbn='978-0201633612',
            publisher='Addison-Wesley',
            publication_year=1994,
            category='Software Engineering',
            quantity=2,
            available_quantity=2
        ),
        Book.objects.create(
            title='Refactoring',
            author='Martin Fowler',
            isbn='978-0201485677',
            publisher='Addison-Wesley',
            publication_year=1999,
            category='Software Engineering',
            quantity=4,
            available_quantity=4
        ),
    ]
    return books


@pytest.fixture
def sample_library_user(db):
    """Creates a sample active library user."""
    return LibraryUser.objects.create(
        full_name='João Silva',
        registration_number='2024001',
        email='joao.silva@test.com',
        phone='11987654321',
        address='Rua A, 123, São Paulo, SP',
        is_active=True
    )


@pytest.fixture
def inactive_library_user(db):
    """Creates an inactive library user."""
    return LibraryUser.objects.create(
        full_name='Maria Santos',
        registration_number='2024002',
        email='maria.santos@test.com',
        phone='11987654322',
        address='Rua B, 456, Rio de Janeiro, RJ',
        is_active=False
    )


@pytest.fixture
def multiple_library_users(db):
    """Creates multiple library users for testing."""
    users = [
        LibraryUser.objects.create(
            full_name='Pedro Costa',
            registration_number='2024003',
            email='pedro.costa@test.com',
            phone='11987654323',
            address='Rua C, 789',
            is_active=True
        ),
        LibraryUser.objects.create(
            full_name='Ana Oliveira',
            registration_number='2024004',
            email='ana.oliveira@test.com',
            phone='11987654324',
            address='Rua D, 101',
            is_active=True
        ),
        LibraryUser.objects.create(
            full_name='Carlos Souza',
            registration_number='2024005',
            email='carlos.souza@test.com',
            phone='11987654325',
            address='Rua E, 202',
            is_active=False
        ),
    ]
    return users


@pytest.fixture
def sample_loan(db, sample_book, sample_library_user):
    """Creates a sample active loan."""
    from datetime import date, timedelta

    loan = Loan.objects.create(
        book=sample_book,
        user=sample_library_user,
        loan_date=date.today(),
        due_date=date.today() + timedelta(days=14)
    )
    return loan


@pytest.fixture
def overdue_loan(db, sample_book, sample_library_user):
    """Creates an overdue loan for testing."""
    from datetime import date, timedelta

    # Create a second book for this loan to avoid conflicts
    overdue_book = Book.objects.create(
        title='Overdue Book',
        author='Test Author',
        isbn='978-9999999999',
        publisher='Test Publisher',
        publication_year=2020,
        category='Fiction',
        quantity=1,
        available_quantity=0
    )

    loan = Loan.objects.create(
        book=overdue_book,
        user=sample_library_user,
        loan_date=date.today() - timedelta(days=20),
        due_date=date.today() - timedelta(days=6)
    )
    return loan


@pytest.fixture
def returned_loan(db, sample_library_user):
    """Creates a returned loan for testing."""
    from datetime import date, timedelta

    # Create a book specifically for this loan
    returned_book = Book.objects.create(
        title='Returned Book',
        author='Test Author',
        isbn='978-8888888888',
        publisher='Test Publisher',
        publication_year=2020,
        category='Fiction',
        quantity=1,
        available_quantity=1
    )

    loan = Loan.objects.create(
        book=returned_book,
        user=sample_library_user,
        loan_date=date.today() - timedelta(days=7),
        due_date=date.today() + timedelta(days=7),
        return_date=date.today()
    )
    return loan
