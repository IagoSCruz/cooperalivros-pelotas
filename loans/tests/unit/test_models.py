"""
Unit tests for Loan model.
"""
import pytest
from datetime import date, timedelta
from freezegun import freeze_time

from loans.models import Loan


@pytest.mark.django_db
@pytest.mark.unit
class TestLoanModel:
    """Test suite for Loan model."""

    def test_create_loan_success(self, sample_book, sample_library_user):
        """Test creating a loan with valid data."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )
        assert loan.id is not None
        assert loan.book == sample_book
        assert loan.user == sample_library_user
        assert loan.status == Loan.LoanStatus.ACTIVE

    def test_loan_str_representation(self, sample_loan):
        """Test loan string representation."""
        expected = f'{sample_loan.book.title} - {sample_loan.user.full_name} ({sample_loan.status})'
        assert str(sample_loan) == expected

    def test_due_date_auto_set_on_save(self, sample_book, sample_library_user):
        """Test due_date is automatically set to 14 days if not provided."""
        loan_date = date(2024, 1, 1)
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=loan_date
            # due_date not provided
        )
        expected_due_date = loan_date + timedelta(days=14)
        assert loan.due_date == expected_due_date

    def test_due_date_not_overridden_if_provided(self, sample_book, sample_library_user):
        """Test due_date is not overridden if explicitly provided."""
        loan_date = date(2024, 1, 1)
        custom_due_date = date(2024, 1, 20)  # 19 days instead of 14

        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=loan_date,
            due_date=custom_due_date
        )
        assert loan.due_date == custom_due_date

    @freeze_time("2024-01-15")
    def test_is_overdue_when_past_due_date(self, sample_book, sample_library_user):
        """Test is_overdue returns True when past due date."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 10)  # 5 days ago
        )
        assert loan.is_overdue() is True

    @freeze_time("2024-01-10")
    def test_is_not_overdue_when_on_due_date(self, sample_book, sample_library_user):
        """Test is_overdue returns False when on due date."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 10)  # Today
        )
        assert loan.is_overdue() is False

    @freeze_time("2024-01-08")
    def test_is_not_overdue_when_before_due_date(self, sample_book, sample_library_user):
        """Test is_overdue returns False when before due date."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)  # 7 days from now
        )
        assert loan.is_overdue() is False

    def test_is_not_overdue_when_returned(self, returned_loan):
        """Test is_overdue returns False for returned loans."""
        # returned_loan fixture is already returned
        assert returned_loan.status == Loan.LoanStatus.RETURNED
        assert returned_loan.is_overdue() is False

    @freeze_time("2024-01-15")
    def test_mark_as_returned(self):
        """Test mark_as_returned sets return_date and status."""
        # Create a separate book to avoid conflicts with fixtures
        from books.models import Book
        book = Book.objects.create(
            title='Return Test Book',
            author='Test Author',
            isbn='9991234567890',
            publisher='Test Publisher',
            publication_year=2020,
            category='Test',
            quantity=1,
            available_quantity=0  # Start with 0 available
        )

        from users.models import LibraryUser
        user = LibraryUser.objects.create(
            full_name='Return Test User',
            email='returntest@test.com',
            registration_number='RET001',
            is_active=True
        )

        loan = Loan.objects.create(
            book=book,
            user=user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)
        )

        assert loan.return_date is None
        assert loan.status == Loan.LoanStatus.ACTIVE
        initial_available = book.available_quantity

        loan.mark_as_returned()

        assert loan.return_date == date(2024, 1, 15)
        assert loan.status == Loan.LoanStatus.RETURNED

        # Verify book copy was returned
        book.refresh_from_db()
        assert book.available_quantity == initial_available + 1

    @freeze_time("2024-01-20")
    def test_days_overdue_when_overdue(self, sample_book, sample_library_user):
        """Test days_overdue returns correct number of days."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)  # 5 days ago
        )
        assert loan.days_overdue() == 5

    @freeze_time("2024-01-10")
    def test_days_overdue_when_not_overdue(self, sample_book, sample_library_user):
        """Test days_overdue returns 0 when not overdue."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)  # 5 days from now
        )
        assert loan.days_overdue() == 0

    def test_days_overdue_when_returned(self, returned_loan):
        """Test days_overdue returns 0 for returned loans."""
        assert returned_loan.days_overdue() == 0

    def test_loan_status_choices(self):
        """Test loan status choices are defined."""
        assert hasattr(Loan.LoanStatus, 'ACTIVE')
        assert hasattr(Loan.LoanStatus, 'RETURNED')
        assert hasattr(Loan.LoanStatus, 'OVERDUE')
        assert hasattr(Loan.LoanStatus, 'RENEWED')

    def test_loan_default_status_is_active(self, sample_book, sample_library_user):
        """Test loan default status is ACTIVE."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )
        assert loan.status == Loan.LoanStatus.ACTIVE

    def test_loan_notes_optional(self, sample_book, sample_library_user):
        """Test notes field is optional."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )
        assert loan.notes == ''

    def test_loan_with_notes(self, sample_book, sample_library_user):
        """Test creating loan with notes."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            notes='Special handling required'
        )
        assert loan.notes == 'Special handling required'

    def test_loan_ordering(self):
        """Test loans are ordered by loan_date descending."""
        from books.models import Book
        from users.models import LibraryUser

        book = Book.objects.create(
            title='Order Test Book',
            author='Test Author',
            isbn='9881234567890',
            publisher='Test Publisher',
            publication_year=2020,
            quantity=5,
            available_quantity=5
        )

        user = LibraryUser.objects.create(
            full_name='Order Test User',
            email='ordertest@test.com',
            registration_number='ORD001',
            is_active=True
        )

        loan1 = Loan.objects.create(
            book=book,
            user=user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)
        )

        loan2 = Loan.objects.create(
            book=book,
            user=user,
            loan_date=date(2024, 1, 10),
            due_date=date(2024, 1, 24)
        )

        loans = list(Loan.objects.filter(book=book))
        assert loans[0].id == loan2.id  # Most recent first
        assert loans[1].id == loan1.id

    def test_loan_relationships(self, sample_loan):
        """Test loan relationships with book and user."""
        assert sample_loan.book is not None
        assert sample_loan.user is not None
        assert sample_loan in sample_loan.book.loans.all()
        assert sample_loan in sample_loan.user.loans.all()

    def test_created_at_auto_set(self, sample_book, sample_library_user):
        """Test created_at is automatically set."""
        loan = Loan.objects.create(
            book=sample_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )
        assert loan.created_at is not None

    def test_updated_at_auto_updated(self, sample_loan):
        """Test updated_at is automatically updated on save."""
        original_updated = sample_loan.updated_at

        sample_loan.notes = 'Updated notes'
        sample_loan.save()
        sample_loan.refresh_from_db()

        assert sample_loan.updated_at > original_updated
