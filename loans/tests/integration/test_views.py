"""
Integration tests for Loans API endpoints.
"""
import pytest
from datetime import date, timedelta
from freezegun import freeze_time
from rest_framework import status

from loans.models import Loan


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetList:
    """Test suite for listing loans."""

    def test_list_loans_returns_all_loans(self, authenticated_client, sample_loan, overdue_loan):
        """Test GET /api/loans/ returns all loans."""
        response = authenticated_client.get('/api/loans/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_list_loans_returns_empty_when_no_loans(self, authenticated_client):
        """Test GET /api/loans/ returns empty list when no loans."""
        response = authenticated_client.get('/api/loans/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_loans_uses_detail_serializer(self, authenticated_client, sample_loan):
        """Test list endpoint uses LoanDetailSerializer with nested data."""
        response = authenticated_client.get('/api/loans/')

        assert response.status_code == status.HTTP_200_OK
        loan_data = response.data[0]

        # Should have nested book and user data
        assert 'book' in loan_data
        assert 'user' in loan_data
        assert isinstance(loan_data['book'], dict)
        assert isinstance(loan_data['user'], dict)
        assert 'title' in loan_data['book']
        assert 'full_name' in loan_data['user']


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetRetrieve:
    """Test suite for retrieving a single loan."""

    def test_retrieve_loan_success(self, authenticated_client, sample_loan):
        """Test GET /api/loans/{id}/ returns loan details."""
        response = authenticated_client.get(f'/api/loans/{sample_loan.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_loan.id

    def test_retrieve_loan_not_found(self, authenticated_client):
        """Test GET /api/loans/{id}/ returns 404 for non-existent loan."""
        response = authenticated_client.get('/api/loans/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_loan_uses_detail_serializer(self, authenticated_client, sample_loan):
        """Test retrieve endpoint uses LoanDetailSerializer."""
        response = authenticated_client.get(f'/api/loans/{sample_loan.id}/')

        assert response.status_code == status.HTTP_200_OK
        # Should have nested book and user
        assert 'book' in response.data
        assert 'user' in response.data
        # Should have computed fields
        assert 'is_overdue' in response.data
        assert 'days_overdue' in response.data


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetCreate:
    """Test suite for creating loans."""

    def test_create_loan_success(self, authenticated_client, sample_book, sample_library_user):
        """Test POST /api/loans/ creates a new loan."""
        initial_available = sample_book.available_quantity

        data = {
            'book': sample_book.id,
            'user': sample_library_user.id,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14))
        }
        response = authenticated_client.post('/api/loans/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['book'] == sample_book.id
        assert response.data['user'] == sample_library_user.id

        # Verify loan was created in database
        assert Loan.objects.filter(book=sample_book, user=sample_library_user).exists()

        # Verify book copy was reserved
        sample_book.refresh_from_db()
        assert sample_book.available_quantity == initial_available - 1

    def test_create_loan_with_unavailable_book(self, authenticated_client, sample_book_with_no_copies, sample_library_user):
        """Test POST /api/loans/ with unavailable book returns 400."""
        data = {
            'book': sample_book_with_no_copies.id,
            'user': sample_library_user.id,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14))
        }
        response = authenticated_client.post('/api/loans/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'book' in response.data

    def test_create_loan_with_inactive_user(self, authenticated_client, sample_book, inactive_library_user):
        """Test POST /api/loans/ with inactive user returns 400."""
        data = {
            'book': sample_book.id,
            'user': inactive_library_user.id,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14))
        }
        response = authenticated_client.post('/api/loans/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'user' in response.data

    def test_create_loan_with_notes(self, authenticated_client, sample_book, sample_library_user):
        """Test POST /api/loans/ with notes."""
        data = {
            'book': sample_book.id,
            'user': sample_library_user.id,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14)),
            'notes': 'Special handling required'
        }
        response = authenticated_client.post('/api/loans/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['notes'] == 'Special handling required'

    def test_create_loan_unauthenticated(self, api_client, sample_book, sample_library_user):
        """Test POST /api/loans/ without authentication returns 401."""
        data = {
            'book': sample_book.id,
            'user': sample_library_user.id,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14))
        }
        response = api_client.post('/api/loans/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetUpdate:
    """Test suite for updating loans."""

    def test_update_loan_success(self, authenticated_client, sample_loan):
        """Test PUT /api/loans/{id}/ updates a loan."""
        data = {
            'book': sample_loan.book.id,
            'user': sample_loan.user.id,
            'loan_date': str(sample_loan.loan_date),
            'due_date': str(sample_loan.due_date),
            'notes': 'Updated notes',
            'status': Loan.LoanStatus.RENEWED
        }
        response = authenticated_client.put(f'/api/loans/{sample_loan.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['notes'] == 'Updated notes'
        assert response.data['status'] == Loan.LoanStatus.RENEWED

        # Verify database was updated
        sample_loan.refresh_from_db()
        assert sample_loan.notes == 'Updated notes'

    def test_partial_update_loan_success(self, authenticated_client, sample_loan):
        """Test PATCH /api/loans/{id}/ partially updates a loan."""
        data = {'notes': 'Partially updated notes'}
        response = authenticated_client.patch(f'/api/loans/{sample_loan.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['notes'] == 'Partially updated notes'

    def test_update_loan_not_found(self, authenticated_client):
        """Test PUT /api/loans/{id}/ returns 404 for non-existent loan."""
        data = {
            'book': 1,
            'user': 1,
            'loan_date': str(date.today()),
            'due_date': str(date.today() + timedelta(days=14))
        }
        response = authenticated_client.put('/api/loans/99999/', data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetDelete:
    """Test suite for deleting loans."""

    def test_delete_loan_success(self, authenticated_client, sample_loan):
        """Test DELETE /api/loans/{id}/ deletes a loan."""
        loan_id = sample_loan.id
        response = authenticated_client.delete(f'/api/loans/{loan_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify loan was deleted
        assert not Loan.objects.filter(id=loan_id).exists()

    def test_delete_loan_not_found(self, authenticated_client):
        """Test DELETE /api/loans/{id}/ returns 404 for non-existent loan."""
        response = authenticated_client.delete('/api/loans/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestLoanViewSetActive:
    """Test suite for active loans endpoint."""

    def test_active_loans_returns_only_active(self, authenticated_client, sample_loan, returned_loan):
        """Test GET /api/loans/active/ returns only active loans."""
        response = authenticated_client.get('/api/loans/active/')

        assert response.status_code == status.HTTP_200_OK

        # Verify sample_loan is in results
        loan_ids = [loan['id'] for loan in response.data]
        assert sample_loan.id in loan_ids
        # Verify returned_loan is not in results
        assert returned_loan.id not in loan_ids

    def test_active_loans_returns_empty_when_none_active(self, authenticated_client, returned_loan):
        """Test GET /api/loans/active/ returns empty when no active loans."""
        response = authenticated_client.get('/api/loans/active/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.integration
@freeze_time("2024-01-20")
class TestLoanViewSetOverdue:
    """Test suite for overdue loans endpoint."""

    def test_overdue_loans_returns_overdue(self, authenticated_client, overdue_loan, sample_loan):
        """Test GET /api/loans/overdue/ returns only overdue loans."""
        response = authenticated_client.get('/api/loans/overdue/')

        assert response.status_code == status.HTTP_200_OK

        loan_ids = [loan['id'] for loan in response.data]
        # overdue_loan should be in results
        assert overdue_loan.id in loan_ids
        # sample_loan should not be in results (not overdue)
        assert sample_loan.id not in loan_ids

    def test_overdue_loans_returns_empty_when_none_overdue(self, authenticated_client, sample_loan):
        """Test GET /api/loans/overdue/ returns empty when no overdue loans."""
        # Only sample_loan exists and it's not overdue
        response = authenticated_client.get('/api/loans/overdue/')

        assert response.status_code == status.HTTP_200_OK
        # sample_loan should not be in results
        loan_ids = [loan['id'] for loan in response.data]
        assert sample_loan.id not in loan_ids


@pytest.mark.django_db
@pytest.mark.integration
@freeze_time("2024-01-15")
class TestLoanViewSetReturnLoan:
    """Test suite for return loan endpoint."""

    def test_return_loan_success(self, authenticated_client):
        """Test POST /api/loans/{id}/return_loan/ marks loan as returned."""
        # Create a fresh book and loan for this test
        from books.models import Book
        from users.models import LibraryUser

        book = Book.objects.create(
            title='Return Test Book',
            author='Test Author',
            isbn='9661234567890',
            publisher='Test Publisher',
            publication_year=2020,
            quantity=1,
            available_quantity=0  # Start with 0 available
        )

        user = LibraryUser.objects.create(
            full_name='Return Test User',
            email='returntest2@test.com',
            registration_number='RET002',
            is_active=True
        )

        loan = Loan.objects.create(
            book=book,
            user=user,
            loan_date=date(2024, 1, 1),
            due_date=date(2024, 1, 15)
        )

        initial_available = book.available_quantity

        response = authenticated_client.post(f'/api/loans/{loan.id}/return_loan/')

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'returned successfully' in response.data['message']

        # Verify loan was marked as returned
        loan.refresh_from_db()
        assert loan.status == Loan.LoanStatus.RETURNED
        assert loan.return_date == date(2024, 1, 15)

        # Verify book copy was returned
        book.refresh_from_db()
        assert book.available_quantity == initial_available + 1

    def test_return_loan_already_returned(self, authenticated_client, returned_loan):
        """Test POST /api/loans/{id}/return_loan/ for already returned loan."""
        response = authenticated_client.post(f'/api/loans/{returned_loan.id}/return_loan/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already been returned' in response.data['message']

    def test_return_loan_not_found(self, authenticated_client):
        """Test POST /api/loans/{id}/return_loan/ for non-existent loan."""
        response = authenticated_client.post('/api/loans/99999/return_loan/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_return_loan_requires_authentication(self, api_client, sample_loan):
        """Test POST /api/loans/{id}/return_loan/ requires authentication."""
        response = api_client.post(f'/api/loans/{sample_loan.id}/return_loan/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
