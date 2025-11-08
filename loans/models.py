"""
Loan models for the library management system.
Follows Django MVC pattern where models represent the data layer.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from books.models import Book
from users.models import LibraryUser


class Loan(models.Model):
    """
    Model representing a book loan.

    Attributes:
        book: Reference to the borrowed book
        user: Reference to the library user who borrowed the book
        loan_date: Date when the book was borrowed
        due_date: Date when the book should be returned
        return_date: Actual date when the book was returned (null if not returned)
        status: Current status of the loan
        notes: Additional notes about the loan
        created_at: Timestamp when the loan was created
        updated_at: Timestamp of last update
    """

    class LoanStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        RETURNED = 'returned', _('Returned')
        OVERDUE = 'overdue', _('Overdue')
        RENEWED = 'renewed', _('Renewed')

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name='loans',
        verbose_name=_('book'),
        help_text=_('Reference to the borrowed book'),
    )
    user = models.ForeignKey(
        LibraryUser,
        on_delete=models.PROTECT,
        related_name='loans',
        verbose_name=_('user'),
        help_text=_('Reference to the library user who borrowed the book'),
    )
    loan_date = models.DateField(
        _('loan date'),
        default=timezone.now,
        help_text=_('Date when the book was borrowed'),
    )
    due_date = models.DateField(
        _('due date'),
        help_text=_('Date when the book should be returned'),
    )
    return_date = models.DateField(
        _('return date'),
        null=True,
        blank=True,
        help_text=_('Actual date when the book was returned'),
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.ACTIVE,
        help_text=_('Current status of the loan'),
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about the loan'),
    )

    # Timestamps
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('loan')
        verbose_name_plural = _('loans')
        ordering = ['-loan_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['loan_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f'{self.book.title} - {self.user.full_name} ({self.status})'

    def save(self, *args, **kwargs):
        """Override save to set due_date if not provided."""
        if not self.due_date:
            # Default loan period is 14 days
            self.due_date = self.loan_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if the loan is overdue."""
        if self.status == self.LoanStatus.RETURNED:
            return False
        return timezone.now().date() > self.due_date

    def mark_as_returned(self):
        """Mark the loan as returned."""
        self.return_date = timezone.now().date()
        self.status = self.LoanStatus.RETURNED
        self.save()
        self.book.return_copy()

    def days_overdue(self):
        """Calculate how many days overdue the loan is."""
        if not self.is_overdue():
            return 0
        return (timezone.now().date() - self.due_date).days
