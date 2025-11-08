"""
Unit tests for LoanRepository.
"""
import pytest
from datetime import date, timedelta
from freezegun import freeze_time

from loans.models import Loan
from loans.repositories.loan_repository import LoanRepository


@pytest.mark.django_db
@pytest.mark.unit
class TestLoanRepository:
    """Test suite for LoanRepository."""

    def test_get_all_returns_all_loans(self, sample_loan, overdue_loan, returned_loan):
        """Test get_all returns all loans in the database."""
        loans = LoanRepository.get_all()
        assert loans.count() >= 3  # At least the 3 fixtures

    def test_get_all_returns_empty_queryset_when_no_loans(self):
        """Test get_all returns empty queryset when no loans exist."""
        loans = LoanRepository.get_all()
        assert loans.count() == 0

    def test_get_by_id_returns_loan_when_exists(self, sample_loan):
        """Test get_by_id returns loan when it exists."""
        loan = LoanRepository.get_by_id(sample_loan.id)
        assert loan is not None
        assert loan.id == sample_loan.id
        assert loan.book == sample_loan.book
        assert loan.user == sample_loan.user

    def test_get_by_id_returns_none_when_not_exists(self):
        """Test get_by_id returns None when loan doesn't exist."""
        loan = LoanRepository.get_by_id(99999)
        assert loan is None

    def test_get_active_loans_returns_only_active(self, sample_loan, returned_loan):
        """Test get_active_loans returns only active loans."""
        loans = LoanRepository.get_active_loans()

        # Check that sample_loan is in results
        assert sample_loan in loans
        # Check that returned_loan is not in results
        assert returned_loan not in loans

        # Verify all returned loans are active
        for loan in loans:
            assert loan.status == Loan.LoanStatus.ACTIVE

    def test_get_active_loans_returns_empty_when_none_active(self, returned_loan):
        """Test get_active_loans returns empty when no active loans."""
        # Only returned_loan exists, so no active loans
        loans = LoanRepository.get_active_loans()
        assert loans.count() == 0

    @freeze_time("2024-01-20")
    def test_get_overdue_loans_returns_overdue(self, overdue_loan, sample_loan):
        """Test get_overdue_loans returns only overdue loans."""
        # overdue_loan has due_date in the past
        # sample_loan has due_date in the future

        loans = LoanRepository.get_overdue_loans()

        # overdue_loan should be in results
        assert overdue_loan in loans
        # sample_loan should not be in results (not overdue)
        assert sample_loan not in loans

    def test_get_overdue_loans_returns_empty_when_none_overdue(self, sample_loan):
        """Test get_overdue_loans returns empty when no overdue loans."""
        # sample_loan is not overdue
        loans = LoanRepository.get_overdue_loans()
        # sample_loan should not be in results
        assert sample_loan not in loans

    def test_get_loans_by_user(self, sample_library_user, sample_loan, overdue_loan):
        """Test get_loans_by_user returns all loans for a user."""
        # Both sample_loan and overdue_loan use sample_library_user
        loans = LoanRepository.get_loans_by_user(sample_library_user.id)

        assert loans.count() >= 2
        assert sample_loan in loans
        assert overdue_loan in loans

    def test_get_loans_by_user_returns_empty_when_no_loans(self, inactive_library_user):
        """Test get_loans_by_user returns empty for user with no loans."""
        loans = LoanRepository.get_loans_by_user(inactive_library_user.id)
        assert loans.count() == 0

    def test_get_loans_by_book(self, sample_book, sample_loan):
        """Test get_loans_by_book returns all loans for a book."""
        loans = LoanRepository.get_loans_by_book(sample_book.id)

        assert sample_loan in loans

    def test_get_loans_by_book_returns_empty_when_no_loans(self, sample_book_with_no_copies):
        """Test get_loans_by_book returns empty for book with no loans."""
        loans = LoanRepository.get_loans_by_book(sample_book_with_no_copies.id)
        assert loans.count() == 0

    def test_get_active_loans_by_user(self, sample_library_user, sample_loan, returned_loan):
        """Test get_active_loans_by_user returns only active loans for user."""
        # Create a returned loan for the same user
        from books.models import Book
        test_book = Book.objects.create(
            title='Active Loan Test Book',
            author='Test Author',
            isbn='9771234567890',
            publisher='Test Publisher',
            publication_year=2020,
            quantity=1,
            available_quantity=1
        )

        active_loan = Loan.objects.create(
            book=test_book,
            user=sample_library_user,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status=Loan.LoanStatus.ACTIVE
        )

        loans = LoanRepository.get_active_loans_by_user(sample_library_user.id)

        assert active_loan in loans
        # Verify all returned loans are active
        for loan in loans:
            assert loan.status == Loan.LoanStatus.ACTIVE
            assert loan.user == sample_library_user

    def test_create_loan_success(self, sample_book, sample_library_user):
        """Test create successfully creates a new loan."""
        data = {
            'book': sample_book,
            'user': sample_library_user,
            'loan_date': date.today(),
            'due_date': date.today() + timedelta(days=14)
        }
        loan = LoanRepository.create(data)

        assert loan.id is not None
        assert loan.book == sample_book
        assert loan.user == sample_library_user
        assert loan.status == Loan.LoanStatus.ACTIVE

        # Verify it was saved to database
        saved_loan = Loan.objects.get(id=loan.id)
        assert saved_loan.book == sample_book

    def test_create_loan_with_notes(self, sample_book, sample_library_user):
        """Test create loan with notes."""
        data = {
            'book': sample_book,
            'user': sample_library_user,
            'loan_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
            'notes': 'Special handling required'
        }
        loan = LoanRepository.create(data)

        assert loan.notes == 'Special handling required'

    def test_update_loan_success(self, sample_loan):
        """Test update successfully updates a loan."""
        data = {
            'notes': 'Updated notes',
            'status': Loan.LoanStatus.RENEWED
        }
        updated_loan = LoanRepository.update(sample_loan, data)

        assert updated_loan.notes == 'Updated notes'
        assert updated_loan.status == Loan.LoanStatus.RENEWED

        # Verify it was saved to database
        sample_loan.refresh_from_db()
        assert sample_loan.notes == 'Updated notes'
        assert sample_loan.status == Loan.LoanStatus.RENEWED

    def test_update_loan_partial_update(self, sample_loan):
        """Test update with partial data updates only specified fields."""
        original_status = sample_loan.status
        data = {'notes': 'New notes only'}
        LoanRepository.update(sample_loan, data)

        sample_loan.refresh_from_db()
        assert sample_loan.notes == 'New notes only'
        assert sample_loan.status == original_status

    def test_delete_loan_success(self, sample_loan):
        """Test delete successfully removes a loan."""
        loan_id = sample_loan.id
        LoanRepository.delete(sample_loan)

        # Verify it was deleted from database
        assert Loan.objects.filter(id=loan_id).count() == 0

    def test_repository_operations_are_transactional(self, sample_book, sample_library_user):
        """Test repository operations maintain data integrity."""
        # Create a loan
        loan = LoanRepository.create({
            'book': sample_book,
            'user': sample_library_user,
            'loan_date': date.today(),
            'due_date': date.today() + timedelta(days=14)
        })

        # Update it
        LoanRepository.update(loan, {'notes': 'Transaction test'})
        loan.refresh_from_db()
        assert loan.notes == 'Transaction test'

        # Delete it
        LoanRepository.delete(loan)
        assert Loan.objects.filter(id=loan.id).count() == 0
