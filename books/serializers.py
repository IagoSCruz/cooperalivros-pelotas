"""
Serializers for Books app.
Handles conversion between model instances and JSON representations.
"""

from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model with full CRUD operations."""

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_year',
            'category',
            'quantity',
            'available_quantity',
            'cover_image',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_isbn(self, value):
        """Validate ISBN format and uniqueness."""
        if not value.isdigit() or len(value) not in [10, 13]:
            raise serializers.ValidationError(
                'ISBN must be 10 or 13 digits'
            )
        return value

    def validate(self, data):
        """Validate that available_quantity <= quantity."""
        quantity = data.get('quantity', getattr(self.instance, 'quantity', None))
        available = data.get(
            'available_quantity',
            getattr(self.instance, 'available_quantity', None),
        )

        if available and quantity and available > quantity:
            raise serializers.ValidationError(
                'Available quantity cannot exceed total quantity'
            )
        return data


class BookListSerializer(serializers.ModelSerializer):
    """Simplified serializer for book listings."""

    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'category',
            'available_quantity',
            'is_available',
            'cover_image',
        ]


class BookBulkUploadSerializer(serializers.Serializer):
    """Serializer for bulk book upload via file."""

    file = serializers.FileField()
    file_type = serializers.ChoiceField(
        choices=['txt', 'excel'],
        help_text='Type of file being uploaded (txt or excel)',
    )

    def validate_file(self, value):
        """Validate file extension and size."""
        file_name = value.name.lower()
        file_type = self.initial_data.get('file_type', '')

        if file_type == 'txt' and not file_name.endswith('.txt'):
            raise serializers.ValidationError('File must be a .txt file')
        elif file_type == 'excel' and not file_name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError(
                'File must be an Excel file (.xlsx or .xls)'
            )

        # Check file size (max 10MB)
        if value.size > 10485760:
            raise serializers.ValidationError('File size cannot exceed 10MB')

        return value
