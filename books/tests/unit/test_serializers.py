"""
Unit tests for Book serializers.
"""
import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from books.serializers import (
    BookSerializer,
    BookListSerializer,
    BookBulkUploadSerializer,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestBookSerializer:
    """Test suite for BookSerializer."""

    def test_serialize_book(self, sample_book):
        """Test serializing a book instance."""
        serializer = BookSerializer(sample_book)
        data = serializer.data

        assert data['id'] == sample_book.id
        assert data['title'] == sample_book.title
        assert data['author'] == sample_book.author
        assert data['isbn'] == sample_book.isbn
        assert data['quantity'] == sample_book.quantity
        assert data['available_quantity'] == sample_book.available_quantity

    def test_deserialize_valid_book_data(self):
        """Test deserializing valid book data."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'publisher': 'Test Publisher',
            'publication_year': 2020,
            'category': 'Fiction',
            'quantity': 5,
            'available_quantity': 5
        }
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()
        book = serializer.save()
        assert book.title == 'Test Book'
        assert book.isbn == '1234567890'

    def test_isbn_validation_requires_digits(self):
        """Test ISBN validation rejects non-numeric values."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '978-01234567',  # Contains hyphens
            'publisher': 'Test Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        serializer = BookSerializer(data=data)
        assert not serializer.is_valid()
        assert 'isbn' in serializer.errors

    def test_isbn_validation_requires_correct_length(self):
        """Test ISBN validation requires 10 or 13 digits."""
        # Too short
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '12345',
            'publisher': 'Test Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        serializer = BookSerializer(data=data)
        assert not serializer.is_valid()
        assert 'isbn' in serializer.errors

        # Too long
        data['isbn'] = '12345678901234'
        serializer = BookSerializer(data=data)
        assert not serializer.is_valid()
        assert 'isbn' in serializer.errors

    def test_isbn_validation_accepts_10_digits(self):
        """Test ISBN validation accepts 10 digits."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'publisher': 'Test Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()

    def test_isbn_validation_accepts_13_digits(self):
        """Test ISBN validation accepts 13 digits."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '9781234567890',
            'publisher': 'Test Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()

    def test_available_quantity_cannot_exceed_quantity(self):
        """Test validation that available_quantity <= quantity."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'publisher': 'Test Publisher',
            'quantity': 5,
            'available_quantity': 10  # Exceeds quantity
        }
        serializer = BookSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_available_quantity_can_equal_quantity(self):
        """Test that available_quantity can equal quantity."""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'publisher': 'Test Publisher',
            'quantity': 5,
            'available_quantity': 5
        }
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()

    def test_update_book_validates_available_quantity(self, sample_book):
        """Test updating a book validates available_quantity."""
        # Try to set available_quantity higher than quantity
        data = {'available_quantity': sample_book.quantity + 1}
        serializer = BookSerializer(sample_book, data=data, partial=True)
        assert not serializer.is_valid()

    def test_read_only_fields_cannot_be_set(self):
        """Test that read-only fields cannot be modified."""
        from datetime import datetime
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'publisher': 'Test Publisher',
            'quantity': 1,
            'available_quantity': 1,
            'id': 9999,  # Should be read-only
            'created_at': datetime.now(),  # Should be read-only
        }
        serializer = BookSerializer(data=data)
        assert serializer.is_valid()
        book = serializer.save()
        assert book.id != 9999  # ID should be auto-generated


@pytest.mark.django_db
@pytest.mark.unit
class TestBookListSerializer:
    """Test suite for BookListSerializer."""

    def test_serialize_book_list(self, sample_book):
        """Test serializing a book for list view."""
        serializer = BookListSerializer(sample_book)
        data = serializer.data

        assert 'id' in data
        assert 'title' in data
        assert 'author' in data
        assert 'isbn' in data
        assert 'category' in data
        assert 'available_quantity' in data
        assert 'is_available' in data

        # Should not include detailed fields
        assert 'publisher' not in data
        assert 'publication_year' not in data
        assert 'created_at' not in data

    def test_is_available_field_reflects_availability(self, sample_book, sample_book_with_no_copies):
        """Test is_available field shows correct availability."""
        # Available book
        serializer = BookListSerializer(sample_book)
        assert serializer.data['is_available'] is True

        # Unavailable book
        serializer = BookListSerializer(sample_book_with_no_copies)
        assert serializer.data['is_available'] is False

    def test_serialize_multiple_books(self, multiple_books):
        """Test serializing multiple books."""
        serializer = BookListSerializer(multiple_books, many=True)
        data = serializer.data

        assert len(data) == 3
        for book_data in data:
            assert 'title' in book_data
            assert 'author' in book_data


@pytest.mark.unit
class TestBookBulkUploadSerializer:
    """Test suite for BookBulkUploadSerializer."""

    def test_valid_txt_file(self):
        """Test validation accepts valid TXT file."""
        file_content = b"Title|Author|ISBN\nTest|Test Author|1234567890"
        file = SimpleUploadedFile("books.txt", file_content, content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = BookBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_valid_excel_file(self):
        """Test validation accepts valid Excel file."""
        # Create a minimal Excel file content
        file = SimpleUploadedFile("books.xlsx", b"fake excel content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = BookBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_txt_file_type_rejects_non_txt_extension(self):
        """Test TXT file type rejects non-.txt files."""
        file = SimpleUploadedFile("books.xlsx", b"content", content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = BookBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_excel_file_type_rejects_non_excel_extension(self):
        """Test Excel file type rejects non-Excel files."""
        file = SimpleUploadedFile("books.txt", b"content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = BookBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_file_size_limit_10mb(self):
        """Test file size cannot exceed 10MB."""
        # Create a file larger than 10MB
        large_content = b"x" * (10485761)  # 10MB + 1 byte
        file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")

        data = {'file': file, 'file_type': 'txt'}
        serializer = BookBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_file_type_choices(self):
        """Test file_type field only accepts 'txt' or 'excel'."""
        file = SimpleUploadedFile("books.txt", b"content", content_type="text/plain")

        # Invalid file_type
        data = {'file': file, 'file_type': 'pdf'}
        serializer = BookBulkUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file_type' in serializer.errors

    def test_xlsx_extension_accepted(self):
        """Test .xlsx extension is accepted for Excel files."""
        file = SimpleUploadedFile("books.xlsx", b"content", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {'file': file, 'file_type': 'excel'}
        serializer = BookBulkUploadSerializer(data=data)
        assert serializer.is_valid()

    def test_xls_extension_accepted(self):
        """Test .xls extension is accepted for Excel files."""
        file = SimpleUploadedFile("books.xls", b"content", content_type="application/vnd.ms-excel")

        data = {'file': file, 'file_type': 'excel'}
        serializer = BookBulkUploadSerializer(data=data)
        assert serializer.is_valid()
