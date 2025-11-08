"""
Views for Books app.
Provides REST API endpoints for CRUD operations and bulk upload.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from books.models import Book
from books.repositories import BookRepository
from books.serializers import (
    BookBulkUploadSerializer,
    BookListSerializer,
    BookSerializer,
)
from books.utils import BookFileProcessor
from rest_framework.parsers import MultiPartParser, FormParser


@extend_schema_view(
    list=extend_schema(summary='List all books', tags=['Books']),
    retrieve=extend_schema(summary='Get book details', tags=['Books']),
    create=extend_schema(summary='Create a new book', tags=['Books']),
    update=extend_schema(summary='Update a book', tags=['Books']),
    partial_update=extend_schema(summary='Partially update a book', tags=['Books']),
    destroy=extend_schema(summary='Delete a book', tags=['Books']),
)
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.

    Provides CRUD operations:
    - GET /api/books/ - List all books
    - POST /api/books/ - Create a new book
    - GET /api/books/{id}/ - Retrieve a specific book
    - PUT /api/books/{id}/ - Update a book
    - PATCH /api/books/{id}/ - Partially update a book
    - DELETE /api/books/{id}/ - Delete a book

    Additional endpoints:
    - GET /api/books/available/ - List available books
    - POST /api/books/bulk_upload/ - Upload books from TXT or Excel file
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    search_fields = ['title', 'author', 'isbn', 'category']
    ordering_fields = ['title', 'author', 'created_at']
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BookListSerializer
        if self.action == 'bulk_upload':
            return BookBulkUploadSerializer
        return BookSerializer

    @extend_schema(
        summary='List available books',
        description='Returns books that have available copies for loan',
        tags=['Books'],
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available books."""
        books = BookRepository.get_available_books()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Bulk upload books',
        description="""
        Upload multiple books from a TXT or Excel file.

        **TXT Format (pipe-delimited):**
        ```
        title|author|isbn|publisher|publication_year|category|quantity
        The Great Gatsby|F. Scott Fitzgerald|9780743273565|Scribner|1925|Fiction|3
        1984|George Orwell|9780451524935|Signet Classic|1949|Fiction|2
        ```

        **Excel Format:**
        Columns: title, author, isbn, publisher, publication_year, category, quantity
        """,
        tags=['Books'],
    )
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload books from TXT or Excel file."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        file_type = serializer.validated_data['file_type']

        result = BookFileProcessor.process_file(file, file_type)

        if result['success']:
            return Response(
                {
                    'message': f'Successfully imported {result["created"]} books',
                    'created': result['created'],
                    'errors': result['errors'],
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    'message': 'Failed to import books',
                    'created': result['created'],
                    'errors': result['errors'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary='Upload book cover image',
        description='Upload or update the cover image for a specific book',
        tags=['Books'],
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cover(self, request, pk=None):
        """Upload cover image for a book."""
        book = self.get_object()

        if 'cover_image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book.cover_image = request.FILES['cover_image']
        book.save()

        serializer = self.get_serializer(book)
        return Response(serializer.data)
