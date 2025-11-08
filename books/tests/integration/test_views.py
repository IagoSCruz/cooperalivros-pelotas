"""
Integration tests for Books API endpoints.
"""
import io
import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from books.models import Book


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetList:
    """Test suite for listing books."""

    def test_list_books_returns_all_books(self, authenticated_client, multiple_books):
        """Test GET /api/books/ returns all books."""
        response = authenticated_client.get('/api/books/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_list_books_returns_empty_when_no_books(self, authenticated_client):
        """Test GET /api/books/ returns empty list when no books."""
        response = authenticated_client.get('/api/books/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_books_uses_list_serializer(self, authenticated_client, sample_book):
        """Test list endpoint uses BookListSerializer."""
        response = authenticated_client.get('/api/books/')

        assert response.status_code == status.HTTP_200_OK
        book_data = response.data[0]

        # BookListSerializer fields
        assert 'id' in book_data
        assert 'title' in book_data
        assert 'author' in book_data
        assert 'isbn' in book_data
        assert 'is_available' in book_data

        # Fields not in BookListSerializer
        assert 'created_at' not in book_data
        assert 'updated_at' not in book_data


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetRetrieve:
    """Test suite for retrieving a single book."""

    def test_retrieve_book_success(self, authenticated_client, sample_book):
        """Test GET /api/books/{id}/ returns book details."""
        response = authenticated_client.get(f'/api/books/{sample_book.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_book.id
        assert response.data['title'] == sample_book.title
        assert response.data['author'] == sample_book.author

    def test_retrieve_book_not_found(self, authenticated_client):
        """Test GET /api/books/{id}/ returns 404 for non-existent book."""
        response = authenticated_client.get('/api/books/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_book_uses_full_serializer(self, authenticated_client, sample_book):
        """Test retrieve endpoint uses BookSerializer with all fields."""
        response = authenticated_client.get(f'/api/books/{sample_book.id}/')

        assert response.status_code == status.HTTP_200_OK
        # Should have all fields from BookSerializer
        assert 'created_at' in response.data
        assert 'updated_at' in response.data
        assert 'quantity' in response.data
        assert 'available_quantity' in response.data


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetCreate:
    """Test suite for creating books."""

    def test_create_book_success(self, authenticated_client):
        """Test POST /api/books/ creates a new book."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1234567890',
            'publisher': 'New Publisher',
            'publication_year': 2023,
            'category': 'Fiction',
            'quantity': 5,
            'available_quantity': 5
        }
        response = authenticated_client.post('/api/books/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Book'
        assert response.data['author'] == 'New Author'

        # Verify book was created in database
        assert Book.objects.filter(isbn='1234567890').exists()

    def test_create_book_invalid_isbn(self, authenticated_client):
        """Test POST /api/books/ with invalid ISBN returns 400."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '12345',  # Too short
            'publisher': 'Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        response = authenticated_client.post('/api/books/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'isbn' in response.data

    def test_create_book_available_exceeds_quantity(self, authenticated_client):
        """Test POST /api/books/ with available > quantity returns 400."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1234567890',
            'publisher': 'Publisher',
            'quantity': 5,
            'available_quantity': 10  # Exceeds quantity
        }
        response = authenticated_client.post('/api/books/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_book_missing_required_fields(self, authenticated_client):
        """Test POST /api/books/ with missing required fields returns 400."""
        data = {
            'title': 'New Book',
            # Missing author, isbn, etc.
        }
        response = authenticated_client.post('/api/books/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'author' in response.data or 'isbn' in response.data

    def test_create_book_unauthenticated(self, api_client):
        """Test POST /api/books/ without authentication returns 401."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1234567890',
            'publisher': 'Publisher',
            'quantity': 1,
            'available_quantity': 1
        }
        response = api_client.post('/api/books/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetUpdate:
    """Test suite for updating books."""

    def test_update_book_success(self, authenticated_client, sample_book):
        """Test PUT /api/books/{id}/ updates a book."""
        data = {
            'title': 'Updated Title',
            'author': 'Updated Author',
            'isbn': sample_book.isbn,  # ISBN must be included
            'publisher': sample_book.publisher,
            'publication_year': sample_book.publication_year,
            'category': sample_book.category,
            'quantity': 10,
            'available_quantity': 10
        }
        response = authenticated_client.put(f'/api/books/{sample_book.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        assert response.data['author'] == 'Updated Author'
        assert response.data['quantity'] == 10

        # Verify database was updated
        sample_book.refresh_from_db()
        assert sample_book.title == 'Updated Title'

    def test_partial_update_book_success(self, authenticated_client, sample_book):
        """Test PATCH /api/books/{id}/ partially updates a book."""
        data = {'title': 'Partially Updated Title'}
        response = authenticated_client.patch(f'/api/books/{sample_book.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Partially Updated Title'
        # Other fields should remain unchanged
        assert response.data['author'] == sample_book.author

    def test_update_book_not_found(self, authenticated_client):
        """Test PUT /api/books/{id}/ returns 404 for non-existent book."""
        data = {
            'title': 'Updated Title',
            'author': 'Updated Author',
            'isbn': '1234567890',
            'quantity': 5,
            'available_quantity': 5
        }
        response = authenticated_client.put('/api/books/99999/', data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetDelete:
    """Test suite for deleting books."""

    def test_delete_book_success(self, authenticated_client, sample_book):
        """Test DELETE /api/books/{id}/ deletes a book."""
        book_id = sample_book.id
        response = authenticated_client.delete(f'/api/books/{book_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify book was deleted
        assert not Book.objects.filter(id=book_id).exists()

    def test_delete_book_not_found(self, authenticated_client):
        """Test DELETE /api/books/{id}/ returns 404 for non-existent book."""
        response = authenticated_client.delete('/api/books/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetAvailable:
    """Test suite for available books endpoint."""

    def test_available_books_returns_only_available(self, authenticated_client, sample_book, sample_book_with_no_copies):
        """Test GET /api/books/available/ returns only available books."""
        response = authenticated_client.get('/api/books/available/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == sample_book.id

    def test_available_books_returns_empty_when_none_available(self, authenticated_client, sample_book_with_no_copies):
        """Test GET /api/books/available/ returns empty when no books available."""
        response = authenticated_client.get('/api/books/available/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_available_books_uses_list_serializer(self, authenticated_client, sample_book):
        """Test available endpoint uses BookListSerializer."""
        response = authenticated_client.get('/api/books/available/')

        assert response.status_code == status.HTTP_200_OK
        book_data = response.data[0]
        assert 'is_available' in book_data


@pytest.mark.django_db
@pytest.mark.integration
class TestBookViewSetBulkUpload:
    """Test suite for bulk upload endpoint."""

    def test_bulk_upload_txt_success(self, authenticated_client):
        """Test POST /api/books/bulk_upload/ with valid TXT file."""
        content = """title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert Martin|9780132350884|Prentice Hall|2008|Software Engineering|5
Refactoring|Martin Fowler|9780201485677|Addison-Wesley|1999|Software Engineering|3"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2
        assert 'Successfully imported' in response.data['message']

        # Verify books were created
        assert Book.objects.count() == 2

    def test_bulk_upload_excel_success(self, authenticated_client):
        """Test POST /api/books/bulk_upload/ with valid Excel file."""
        data_rows = [
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

        df = pd.DataFrame(data_rows)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        file = SimpleUploadedFile("books.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        data = {
            'file': file,
            'file_type': 'excel'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 2
        assert Book.objects.count() == 2

    def test_bulk_upload_invalid_file_type(self, authenticated_client):
        """Test POST /api/books/bulk_upload/ with invalid file type."""
        file = SimpleUploadedFile("books.txt", b"content", content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'invalid'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_upload_wrong_file_extension(self, authenticated_client):
        """Test POST /api/books/bulk_upload/ with wrong file extension."""
        file = SimpleUploadedFile("books.pdf", b"content", content_type="application/pdf")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_upload_invalid_content(self, authenticated_client):
        """Test POST /api/books/bulk_upload/ with invalid content."""
        content = """wrong|header
data|here"""
        file = SimpleUploadedFile("books.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['created'] == 0

    def test_bulk_upload_partial_success(self, authenticated_client, sample_book):
        """Test bulk upload with some valid and some invalid rows."""
        content = f"""title|author|isbn|publisher|publication_year|category|quantity
New Book|New Author|1234567890|Publisher|2020|Fiction|5
Duplicate|Author|{sample_book.isbn}|Publisher|2020|Fiction|3"""

        file = SimpleUploadedFile("books.txt", content.encode('utf-8'), content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = authenticated_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['created'] == 1
        assert len(response.data['errors']) > 0

    def test_bulk_upload_requires_authentication(self, api_client):
        """Test POST /api/books/bulk_upload/ requires authentication."""
        file = SimpleUploadedFile("books.txt", b"content", content_type="text/plain")
        data = {
            'file': file,
            'file_type': 'txt'
        }
        response = api_client.post('/api/books/bulk_upload/', data, format='multipart')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
