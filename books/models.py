"""
Book models for the library management system.
Follows Django MVC pattern where models represent the data layer.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    """
    Model representing a book in the library collection.

    Attributes:
        title: The title of the book
        author: The author(s) of the book
        isbn: International Standard Book Number (unique identifier)
        publisher: Publishing company
        publication_year: Year the book was published
        category: Genre or category of the book
        quantity: Total copies available in the library
        available_quantity: Number of copies currently available for loan
        created_at: Timestamp when the book was added to the system
        updated_at: Timestamp of last update
    """

    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_('The title of the book'),
    )
    author = models.CharField(
        _('author'),
        max_length=255,
        help_text=_('The author(s) of the book'),
    )
    isbn = models.CharField(
        _('ISBN'),
        max_length=13,
        unique=True,
        help_text=_('International Standard Book Number'),
    )
    publisher = models.CharField(
        _('publisher'),
        max_length=255,
        blank=True,
        help_text=_('Publishing company'),
    )
    publication_year = models.PositiveIntegerField(
        _('publication year'),
        null=True,
        blank=True,
        help_text=_('Year the book was published'),
    )
    category = models.CharField(
        _('category'),
        max_length=100,
        blank=True,
        help_text=_('Genre or category of the book'),
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        help_text=_('Total copies available in the library'),
    )
    available_quantity = models.PositiveIntegerField(
        _('available quantity'),
        default=1,
        help_text=_('Number of copies currently available for loan'),
    )
    cover_image = models.ImageField(
        _('cover image'),
        upload_to='books/covers/',
        blank=True,
        null=True,
        help_text=_('Book cover image'),
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
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ['title']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f'{self.title} by {self.author}'

    def is_available(self):
        """Check if the book is available for loan."""
        return self.available_quantity > 0

    def reserve_copy(self):
        """Reserve a copy of the book for loan."""
        if self.available_quantity > 0:
            self.available_quantity -= 1
            self.save()
            return True
        return False

    def return_copy(self):
        """Return a copy of the book."""
        if self.available_quantity < self.quantity:
            self.available_quantity += 1
            self.save()
            return True
        return False
