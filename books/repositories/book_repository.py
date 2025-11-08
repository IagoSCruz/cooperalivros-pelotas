"""
Repository pattern implementation for Book model.
This layer abstracts data access, allowing for future migration from TXT to database.
"""

from typing import Optional

from django.db.models import QuerySet

from books.models import Book


class BookRepository:
    """
    Repository for Book model operations.

    This repository provides an abstraction layer over data access,
    making it easier to switch between different storage backends
    (TXT files, SQLite, PostgreSQL, etc.).
    """

    @staticmethod
    def get_all() -> QuerySet[Book]:
        """Retrieve all books from the repository."""
        return Book.objects.all()

    @staticmethod
    def get_by_id(book_id: int) -> Optional[Book]:
        """
        Retrieve a book by its ID.

        Args:
            book_id: The ID of the book to retrieve

        Returns:
            Book instance if found, None otherwise
        """
        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return None

    @staticmethod
    def get_by_isbn(isbn: str) -> Optional[Book]:
        """
        Retrieve a book by its ISBN.

        Args:
            isbn: The ISBN of the book to retrieve

        Returns:
            Book instance if found, None otherwise
        """
        try:
            return Book.objects.get(isbn=isbn)
        except Book.DoesNotExist:
            return None

    @staticmethod
    def search_by_title(title: str) -> QuerySet[Book]:
        """
        Search books by title (case-insensitive partial match).

        Args:
            title: The title or partial title to search for

        Returns:
            QuerySet of matching books
        """
        return Book.objects.filter(title__icontains=title)

    @staticmethod
    def search_by_author(author: str) -> QuerySet[Book]:
        """
        Search books by author (case-insensitive partial match).

        Args:
            author: The author name or partial name to search for

        Returns:
            QuerySet of matching books
        """
        return Book.objects.filter(author__icontains=author)

    @staticmethod
    def get_available_books() -> QuerySet[Book]:
        """Retrieve all books that are currently available for loan."""
        return Book.objects.filter(available_quantity__gt=0)

    @staticmethod
    def create(data: dict) -> Book:
        """
        Create a new book in the repository.

        Args:
            data: Dictionary containing book data

        Returns:
            Created Book instance
        """
        return Book.objects.create(**data)

    @staticmethod
    def update(book: Book, data: dict) -> Book:
        """
        Update an existing book.

        Args:
            book: Book instance to update
            data: Dictionary containing updated data

        Returns:
            Updated Book instance
        """
        for key, value in data.items():
            setattr(book, key, value)
        book.save()
        return book

    @staticmethod
    def delete(book: Book) -> None:
        """
        Delete a book from the repository.

        Args:
            book: Book instance to delete
        """
        book.delete()

    @staticmethod
    def filter_by_category(category: str) -> QuerySet[Book]:
        """
        Filter books by category.

        Args:
            category: The category to filter by

        Returns:
            QuerySet of books in the specified category
        """
        return Book.objects.filter(category__iexact=category)
