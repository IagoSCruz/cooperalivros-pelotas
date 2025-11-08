"""
Repository pattern implementation for LibraryUser model.
"""

from typing import Optional

from django.db.models import QuerySet

from users.models import LibraryUser


class UserRepository:
    """Repository for LibraryUser model operations."""

    @staticmethod
    def get_all() -> QuerySet[LibraryUser]:
        """Retrieve all library users."""
        return LibraryUser.objects.all()

    @staticmethod
    def get_by_id(user_id: int) -> Optional[LibraryUser]:
        """Retrieve a user by ID."""
        try:
            return LibraryUser.objects.get(id=user_id)
        except LibraryUser.DoesNotExist:
            return None

    @staticmethod
    def get_by_registration_number(registration_number: str) -> Optional[LibraryUser]:
        """Retrieve a user by registration number."""
        try:
            return LibraryUser.objects.get(registration_number=registration_number)
        except LibraryUser.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[LibraryUser]:
        """Retrieve a user by email."""
        try:
            return LibraryUser.objects.get(email=email)
        except LibraryUser.DoesNotExist:
            return None

    @staticmethod
    def get_active_users() -> QuerySet[LibraryUser]:
        """Retrieve all active users."""
        return LibraryUser.objects.filter(is_active=True)

    @staticmethod
    def search_by_name(name: str) -> QuerySet[LibraryUser]:
        """Search users by name (case-insensitive partial match)."""
        return LibraryUser.objects.filter(full_name__icontains=name)

    @staticmethod
    def create(data: dict) -> LibraryUser:
        """Create a new library user."""
        return LibraryUser.objects.create(**data)

    @staticmethod
    def update(user: LibraryUser, data: dict) -> LibraryUser:
        """Update an existing user."""
        for key, value in data.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete(user: LibraryUser) -> None:
        """Delete a user."""
        user.delete()
