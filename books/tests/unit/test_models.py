"""
Unit tests for Book model.
"""
import pytest
from django.core.exceptions import ValidationError

from books.models import Book


@pytest.mark.django_db
@pytest.mark.unit
class TestBookModel:
    """Test suite for Book model."""

    def test_create_book_success(self):
        """Test creating a book with valid data."""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='978-0132350884',
            publisher='Test Publisher',
            publication_year=2020,
            quantity=5,
            available_quantity=5
        )
        assert book.id is not None
        assert book.title == 'Test Book'
        assert book.author == 'Test Author'
        assert book.isbn == '978-0132350884'
        assert book.quantity == 5
        assert book.available_quantity == 5

    def test_book_str_representation(self):
        """Test book string representation."""
        book = Book.objects.create(
            title='Clean Code',
            author='Robert Martin',
            isbn='978-0132350884',
            publisher='Prentice Hall',
            publication_year=2008,
            quantity=3,
            available_quantity=3
        )
        assert str(book) == 'Clean Code by Robert Martin'

    def test_is_available_with_copies(self, sample_book):
        """Test is_available returns True when copies are available."""
        assert sample_book.is_available() is True
        assert sample_book.available_quantity > 0

    def test_is_available_without_copies(self, sample_book_with_no_copies):
        """Test is_available returns False when no copies available."""
        assert sample_book_with_no_copies.is_available() is False
        assert sample_book_with_no_copies.available_quantity == 0

    def test_reserve_copy_success(self, sample_book):
        """Test reserving a copy decreases available_quantity."""
        initial_available = sample_book.available_quantity
        result = sample_book.reserve_copy()
        sample_book.refresh_from_db()
        assert result is True
        assert sample_book.available_quantity == initial_available - 1

    def test_reserve_copy_when_unavailable(self, sample_book_with_no_copies):
        """Test reserving a copy when none available returns False."""
        result = sample_book_with_no_copies.reserve_copy()
        assert result is False
        sample_book_with_no_copies.refresh_from_db()
        assert sample_book_with_no_copies.available_quantity == 0

    def test_return_copy_success(self, sample_book):
        """Test returning a copy increases available_quantity."""
        sample_book.reserve_copy()
        initial_available = sample_book.available_quantity
        result = sample_book.return_copy()
        sample_book.refresh_from_db()
        assert result is True
        assert sample_book.available_quantity == initial_available + 1

    def test_return_copy_when_at_max(self, sample_book):
        """Test returning a copy when at max quantity returns False."""
        # Sample book starts with all copies available
        result = sample_book.return_copy()
        assert result is False

    def test_multiple_reserve_and_return_operations(self, sample_book):
        """Test multiple reserve and return operations."""
        initial_available = sample_book.available_quantity

        # Reserve 2 copies
        sample_book.reserve_copy()
        sample_book.reserve_copy()
        sample_book.refresh_from_db()
        assert sample_book.available_quantity == initial_available - 2

        # Return 1 copy
        sample_book.return_copy()
        sample_book.refresh_from_db()
        assert sample_book.available_quantity == initial_available - 1

        # Return another copy
        sample_book.return_copy()
        sample_book.refresh_from_db()
        assert sample_book.available_quantity == initial_available

    def test_book_fields_constraints(self):
        """Test book field constraints."""
        # Test title max length
        with pytest.raises(Exception):
            Book.objects.create(
                title='A' * 300,  # Exceeds max_length
                author='Test Author',
                isbn='978-0132350884',
                publisher='Test Publisher',
                publication_year=2020,
                quantity=1,
                available_quantity=1
            )

    def test_isbn_uniqueness(self, sample_book):
        """Test ISBN must be unique."""
        with pytest.raises(Exception):
            Book.objects.create(
                title='Different Book',
                author='Different Author',
                isbn=sample_book.isbn,  # Duplicate ISBN
                publisher='Test Publisher',
                publication_year=2020,
                quantity=1,
                available_quantity=1
            )

    def test_quantity_cannot_be_negative(self):
        """Test quantity cannot be negative."""
        with pytest.raises(ValidationError):
            book = Book(
                title='Test Book',
                author='Test Author',
                isbn='978-1234567890',
                publisher='Test Publisher',
                publication_year=2020,
                quantity=-1,
                available_quantity=0
            )
            book.full_clean()

    def test_book_category_field(self):
        """Test book category field."""
        book = Book.objects.create(
            title='Python Programming',
            author='John Doe',
            isbn='978-1111111111',
            publisher='Tech Publisher',
            publication_year=2023,
            category='Programming',
            quantity=3,
            available_quantity=3
        )
        assert book.category == 'Programming'

    def test_book_ordering(self):
        """Test books are ordered by title by default."""
        Book.objects.create(
            title='Zebra Book',
            author='Author Z',
            isbn='978-2222222222',
            publisher='Publisher',
            publication_year=2020,
            quantity=1,
            available_quantity=1
        )
        Book.objects.create(
            title='Alpha Book',
            author='Author A',
            isbn='978-3333333333',
            publisher='Publisher',
            publication_year=2020,
            quantity=1,
            available_quantity=1
        )

        books = list(Book.objects.all())
        assert books[0].title == 'Alpha Book'
        assert books[1].title == 'Zebra Book'
