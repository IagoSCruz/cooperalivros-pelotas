"""
Repository pattern implementation for Loan model.
"""

from typing import Optional

from django.db.models import QuerySet
from django.utils import timezone

from loans.models import Loan


class LoanRepository:
    """Repository for Loan model operations."""

    @staticmethod
    def get_all() -> QuerySet[Loan]:
        """Retrieve all loans."""
        return Loan.objects.all()

    @staticmethod
    def get_by_id(loan_id: int) -> Optional[Loan]:
        """Retrieve a loan by ID."""
        try:
            return Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return None

    @staticmethod
    def get_active_loans() -> QuerySet[Loan]:
        """Retrieve all active loans."""
        return Loan.objects.filter(status=Loan.LoanStatus.ACTIVE)

    @staticmethod
    def get_overdue_loans() -> QuerySet[Loan]:
        """Retrieve all overdue loans."""
        return Loan.objects.filter(
            status=Loan.LoanStatus.ACTIVE, due_date__lt=timezone.now().date()
        )

    @staticmethod
    def get_loans_by_user(user_id: int) -> QuerySet[Loan]:
        """Retrieve all loans for a specific user."""
        return Loan.objects.filter(user_id=user_id)

    @staticmethod
    def get_loans_by_book(book_id: int) -> QuerySet[Loan]:
        """Retrieve all loans for a specific book."""
        return Loan.objects.filter(book_id=book_id)

    @staticmethod
    def get_active_loans_by_user(user_id: int) -> QuerySet[Loan]:
        """Retrieve active loans for a specific user."""
        return Loan.objects.filter(user_id=user_id, status=Loan.LoanStatus.ACTIVE)

    @staticmethod
    def create(data: dict) -> Loan:
        """Create a new loan."""
        return Loan.objects.create(**data)

    @staticmethod
    def update(loan: Loan, data: dict) -> Loan:
        """Update an existing loan."""
        for key, value in data.items():
            setattr(loan, key, value)
        loan.save()
        return loan

    @staticmethod
    def delete(loan: Loan) -> None:
        """Delete a loan."""
        loan.delete()
