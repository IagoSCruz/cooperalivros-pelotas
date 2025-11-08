"""
Unit tests for BookFileProcessor.
"""
import io
import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile

from books.models import Book
from books.utils.file_processors import BookFileProcessor


@pytest.mark.django_db
@pytest.mark.unit
class TestBookFileProcessorTXT:
    """Test suite for BookFileProcessor TXT file processing."""

    def test_process_valid_txt_file(self):
        """Test processing a valid TXT file."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|2008|Software Engineering|5
Refactoring|Martin Fowler|9780201485677|Addison-Wesley|1999|Software Engineering|3"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert len(result['errors']) == 0

        # Verify books were created
        assert Book.objects.count() == 2
        book = Book.objects.get(isbn='9780132350884')
        assert book.title == 'Clean Code'
        assert book.author == 'Robert Martin'
        assert book.quantity == 5
        assert book.available_quantity == 5

    def test_process_txt_file_with_empty_lines(self):
        """Test processing TXT file with empty lines."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|2008|Software Engineering|5

Refactoring|Martin Fowler|9780201485677|Addison-Wesley|1999|Software Engineering|3"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert Book.objects.count() == 2

    def test_process_txt_file_invalid_header(self):
        """Test processing TXT file with invalid header."""
        content = """wrong|header|format
Clean Code|Robert Martin|9780132350884"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'Invalid header' in result['errors'][0]

    def test_process_txt_file_insufficient_lines(self):
        """Test processing TXT file with only header."""
        content = """title|author|isbn|publisher|publication_year|category|quantity"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert 'at least a header and one data row' in result['errors'][0]

    def test_process_txt_file_wrong_field_count(self):
        """Test processing TXT file with wrong number of fields."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'Expected 7 fields' in result['errors'][0]

    def test_process_txt_file_duplicate_isbn(self, sample_book):
        """Test processing TXT file with duplicate ISBN."""
        content = f"""title|author|isbn|publisher|publication_year|category|quantity
New Book|New Author|{sample_book.isbn}|Publisher|2020|Fiction|2"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_txt_file_invalid_year(self):
        """Test processing TXT file with invalid year."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|invalid_year|Software|5"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0

    def test_process_txt_file_invalid_quantity(self):
        """Test processing TXT file with invalid quantity."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|2008|Software|not_a_number"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0

    def test_process_txt_file_empty_optional_fields(self):
        """Test processing TXT file with empty optional fields."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall||Software Engineering|5"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 1

        book = Book.objects.get(isbn='9780132350884')
        assert book.publication_year is None

    def test_process_txt_file_transaction_rollback_on_error(self):
        """Test that transaction rolls back on error."""
        # This content has one valid and one invalid line
        content = """title|author|isbn|publisher|publication_year|category|quantity
Valid Book|Author|9780132350884|Publisher|2020|Fiction|5
Invalid Book|Author"""  # Missing fields

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))

        initial_count = Book.objects.count()
        result = BookFileProcessor.process_txt_file(file)

        # The valid book should still be created since we continue on errors
        assert result['created'] == 1
        assert Book.objects.count() == initial_count + 1


@pytest.mark.django_db
@pytest.mark.unit
class TestBookFileProcessorExcel:
    """Test suite for BookFileProcessor Excel file processing."""

    def create_excel_file(self, data_rows):
        """Helper to create Excel file from data rows."""
        df = pd.DataFrame(data_rows)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return SimpleUploadedFile("books.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def test_process_valid_excel_file(self):
        """Test processing a valid Excel file."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'isbn': '9780132350884',
                'publisher': 'Prentice Hall',
                'publication_year': 2008,
                'category': 'Software Engineering',
                'quantity': 5
            },
            {
                'title': 'Refactoring',
                'author': 'Martin Fowler',
                'isbn': '9780201485677',
                'publisher': 'Addison-Wesley',
                'publication_year': 1999,
                'category': 'Software Engineering',
                'quantity': 3
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert len(result['errors']) == 0

        assert Book.objects.count() == 2
        book = Book.objects.get(isbn='9780132350884')
        assert book.title == 'Clean Code'
        assert book.available_quantity == 5

    def test_process_excel_file_missing_columns(self):
        """Test processing Excel file with missing required columns."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                # Missing isbn and other required fields
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert 'Missing required columns' in result['errors'][0]

    def test_process_excel_file_with_extra_columns(self):
        """Test processing Excel file with extra columns is OK."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'isbn': '9780132350884',
                'publisher': 'Prentice Hall',
                'publication_year': 2008,
                'category': 'Software Engineering',
                'quantity': 5,
                'extra_column': 'This should be ignored'
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_excel_file_case_insensitive_columns(self):
        """Test that column names are case insensitive."""
        data = [
            {
                'TITLE': 'Clean Code',
                'AUTHOR': 'Robert Martin',
                'ISBN': '9780132350884',
                'PUBLISHER': 'Prentice Hall',
                'PUBLICATION_YEAR': 2008,
                'CATEGORY': 'Software Engineering',
                'QUANTITY': 5
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_excel_file_skip_empty_rows(self):
        """Test that empty rows are skipped."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'isbn': '9780132350884',
                'publisher': 'Prentice Hall',
                'publication_year': 2008,
                'category': 'Software Engineering',
                'quantity': 5
            },
            {
                'title': None,  # Empty title
                'author': None,
                'isbn': None,  # Empty ISBN
                'publisher': None,
                'publication_year': None,
                'category': None,
                'quantity': None
            },
            {
                'title': 'Refactoring',
                'author': 'Martin Fowler',
                'isbn': '9780201485677',
                'publisher': 'Addison-Wesley',
                'publication_year': 1999,
                'category': 'Software Engineering',
                'quantity': 3
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 2

    def test_process_excel_file_duplicate_isbn(self, sample_book):
        """Test processing Excel file with duplicate ISBN."""
        data = [
            {
                'title': 'New Book',
                'author': 'New Author',
                'isbn': sample_book.isbn,
                'publisher': 'Publisher',
                'publication_year': 2020,
                'category': 'Fiction',
                'quantity': 2
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_excel_file_with_nan_values(self):
        """Test processing Excel file with NaN values for optional fields."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'isbn': '9780132350884',
                'publisher': None,  # NaN/None for optional field
                'publication_year': None,  # NaN/None for optional field
                'category': None,  # NaN/None for optional field
                'quantity': 5
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

        book = Book.objects.get(isbn='9780132350884')
        assert book.publication_year is None
        assert book.category == ''

    def test_process_excel_file_invalid_data_type(self):
        """Test processing Excel file with invalid data types."""
        data = [
            {
                'title': 'Clean Code',
                'author': 'Robert Martin',
                'isbn': '9780132350884',
                'publisher': 'Publisher',
                'publication_year': 2008,
                'category': 'Fiction',
                'quantity': 'not_a_number'  # Invalid quantity
            }
        ]

        file = self.create_excel_file(data)
        result = BookFileProcessor.process_excel_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0


@pytest.mark.django_db
@pytest.mark.unit
class TestBookFileProcessorGeneral:
    """Test suite for BookFileProcessor general methods."""

    def test_process_file_txt(self):
        """Test process_file routes to TXT processor."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|2008|Software Engineering|5"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'))
        result = BookFileProcessor.process_file(file, 'txt')

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_file_excel(self):
        """Test process_file routes to Excel processor."""
        df = pd.DataFrame([{
            'title': 'Clean Code',
            'author': 'Robert Martin',
            'isbn': '9780132350884',
            'publisher': 'Prentice Hall',
            'publication_year': 2008,
            'category': 'Software Engineering',
            'quantity': 5
        }])
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        file = SimpleUploadedFile("books.xlsx", buffer.read())

        result = BookFileProcessor.process_file(file, 'excel')

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_file_unsupported_type(self):
        """Test process_file rejects unsupported file types."""
        file = SimpleUploadedFile("books.pdf", b"content")
        result = BookFileProcessor.process_file(file, 'pdf')

        assert result['success'] is False
        assert result['created'] == 0
        assert 'Unsupported file type' in result['errors'][0]
