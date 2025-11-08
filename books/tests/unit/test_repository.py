"""
Unit tests for BookRepository.
"""
import pytest

from books.models import Book
from books.repositories.book_repository import BookRepository


@pytest.mark.django_db
@pytest.mark.unit
class TestBookRepository:
    """Test suite for BookRepository."""

    def test_get_all_returns_all_books(self, multiple_books):
        """Test get_all returns all books in the database."""
        books = BookRepository.get_all()
        assert books.count() == 3
        # Check they're ordered by title (default ordering)
        titles = [book.title for book in books]
        assert titles == sorted(titles)

    def test_get_all_returns_empty_queryset_when_no_books(self):
        """Test get_all returns empty queryset when no books exist."""
        books = BookRepository.get_all()
        assert books.count() == 0

    def test_get_by_id_returns_book_when_exists(self, sample_book):
        """Test get_by_id returns book when it exists."""
        book = BookRepository.get_by_id(sample_book.id)
        assert book is not None
        assert book.id == sample_book.id
        assert book.title == sample_book.title

    def test_get_by_id_returns_none_when_not_exists(self):
        """Test get_by_id returns None when book doesn't exist."""
        book = BookRepository.get_by_id(99999)
        assert book is None

    def test_get_by_isbn_returns_book_when_exists(self, sample_book):
        """Test get_by_isbn returns book when it exists."""
        book = BookRepository.get_by_isbn(sample_book.isbn)
        assert book is not None
        assert book.isbn == sample_book.isbn
        assert book.title == sample_book.title

    def test_get_by_isbn_returns_none_when_not_exists(self):
        """Test get_by_isbn returns None when ISBN doesn't exist."""
        book = BookRepository.get_by_isbn('978-0000000000')
        assert book is None

    def test_search_by_title_finds_exact_match(self, sample_book):
        """Test search_by_title finds exact title match."""
        books = BookRepository.search_by_title('Clean Code')
        assert books.count() == 1
        assert books.first().title == 'Clean Code'

    def test_search_by_title_finds_partial_match(self, multiple_books):
        """Test search_by_title finds partial matches."""
        books = BookRepository.search_by_title('Programmer')
        assert books.count() == 1
        assert 'Programmer' in books.first().title

    def test_search_by_title_is_case_insensitive(self, sample_book):
        """Test search_by_title is case insensitive."""
        books = BookRepository.search_by_title('clean code')
        assert books.count() == 1
        books = BookRepository.search_by_title('CLEAN CODE')
        assert books.count() == 1

    def test_search_by_title_returns_empty_when_no_match(self):
        """Test search_by_title returns empty queryset when no match."""
        books = BookRepository.search_by_title('Nonexistent Book')
        assert books.count() == 0

    def test_search_by_author_finds_exact_match(self, sample_book):
        """Test search_by_author finds exact author match."""
        books = BookRepository.search_by_author('Robert C. Martin')
        assert books.count() == 1
        assert books.first().author == 'Robert C. Martin'

    def test_search_by_author_finds_partial_match(self, multiple_books):
        """Test search_by_author finds partial matches."""
        books = BookRepository.search_by_author('Fowler')
        assert books.count() == 1
        assert 'Fowler' in books.first().author

    def test_search_by_author_is_case_insensitive(self, sample_book):
        """Test search_by_author is case insensitive."""
        books = BookRepository.search_by_author('robert martin')
        assert books.count() == 1
        books = BookRepository.search_by_author('ROBERT MARTIN')
        assert books.count() == 1

    def test_search_by_author_returns_empty_when_no_match(self):
        """Test search_by_author returns empty queryset when no match."""
        books = BookRepository.search_by_author('Nonexistent Author')
        assert books.count() == 0

    def test_get_available_books_returns_only_available(self, sample_book, sample_book_with_no_copies):
        """Test get_available_books returns only books with available copies."""
        books = BookRepository.get_available_books()
        assert books.count() == 1
        assert books.first().id == sample_book.id
        assert books.first().available_quantity > 0

    def test_get_available_books_returns_empty_when_none_available(self, sample_book_with_no_copies):
        """Test get_available_books returns empty when no books available."""
        books = BookRepository.get_available_books()
        assert books.count() == 0

    def test_create_book_success(self):
        """Test create successfully creates a new book."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '978-4444444444',
            'publisher': 'New Publisher',
            'publication_year': 2023,
            'category': 'Fiction',
            'quantity': 2,
            'available_quantity': 2
        }
        book = BookRepository.create(data)
        assert book.id is not None
        assert book.title == 'New Book'
        assert book.author == 'New Author'
        assert book.isbn == '978-4444444444'

        # Verify it was saved to database
        saved_book = Book.objects.get(id=book.id)
        assert saved_book.title == 'New Book'

    def test_update_book_success(self, sample_book):
        """Test update successfully updates a book."""
        data = {
            'title': 'Updated Title',
            'author': 'Updated Author'
        }
        updated_book = BookRepository.update(sample_book, data)
        assert updated_book.title == 'Updated Title'
        assert updated_book.author == 'Updated Author'
        assert updated_book.isbn == sample_book.isbn  # Unchanged field

        # Verify it was saved to database
        sample_book.refresh_from_db()
        assert sample_book.title == 'Updated Title'
        assert sample_book.author == 'Updated Author'

    def test_update_book_partial_update(self, sample_book):
        """Test update with partial data updates only specified fields."""
        original_author = sample_book.author
        data = {'title': 'New Title Only'}
        BookRepository.update(sample_book, data)

        sample_book.refresh_from_db()
        assert sample_book.title == 'New Title Only'
        assert sample_book.author == original_author

    def test_delete_book_success(self, sample_book):
        """Test delete successfully removes a book."""
        book_id = sample_book.id
        BookRepository.delete(sample_book)

        # Verify it was deleted from database
        assert Book.objects.filter(id=book_id).count() == 0

    def test_filter_by_category_returns_matching_books(self, multiple_books):
        """Test filter_by_category returns books in specified category."""
        books = BookRepository.filter_by_category('Software Engineering')
        assert books.count() == 3
        for book in books:
            assert book.category == 'Software Engineering'

    def test_filter_by_category_is_case_insensitive(self):
        """Test filter_by_category is case insensitive."""
        Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='978-5555555555',
            publisher='Test Publisher',
            publication_year=2020,
            category='Fiction',
            quantity=1,
            available_quantity=1
        )

        books = BookRepository.filter_by_category('fiction')
        assert books.count() == 1
        books = BookRepository.filter_by_category('FICTION')
        assert books.count() == 1

    def test_filter_by_category_returns_empty_when_no_match(self):
        """Test filter_by_category returns empty when no match."""
        books = BookRepository.filter_by_category('Nonexistent Category')
        assert books.count() == 0

    def test_repository_operations_are_transactional(self):
        """Test repository operations maintain data integrity."""
        # Create a book
        book = BookRepository.create({
            'title': 'Transaction Test',
            'author': 'Test Author',
            'isbn': '978-6666666666',
            'publisher': 'Test Publisher',
            'publication_year': 2020,
            'quantity': 5,
            'available_quantity': 5
        })

        # Update it
        BookRepository.update(book, {'quantity': 10})
        book.refresh_from_db()
        assert book.quantity == 10

        # Delete it
        BookRepository.delete(book)
        assert Book.objects.filter(isbn='978-6666666666').count() == 0
