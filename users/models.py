"""
User models for the library management system.
Follows Django MVC pattern where models represent the data layer.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class LibraryUser(models.Model):
    """
    Model representing a library user (patron).

    Attributes:
        full_name: Complete name of the user
        email: Email address for communication
        phone: Contact phone number
        address: Physical address
        registration_number: Unique identifier for the library user
        is_active: Whether the user can borrow books
        created_at: Timestamp when the user registered
        updated_at: Timestamp of last update
    """

    full_name = models.CharField(
        _('full name'),
        max_length=255,
        help_text=_('Complete name of the user'),
    )
    email = models.EmailField(
        _('email'),
        unique=True,
        help_text=_('Email address for communication'),
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        help_text=_('Contact phone number'),
    )
    address = models.TextField(
        _('address'),
        blank=True,
        help_text=_('Physical address'),
    )
    registration_number = models.CharField(
        _('registration number'),
        max_length=50,
        unique=True,
        help_text=_('Unique identifier for the library user'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether the user can borrow books'),
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
        verbose_name = _('library user')
        verbose_name_plural = _('library users')
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.registration_number})'

    def can_borrow(self):
        """Check if the user can borrow books."""
        return self.is_active
