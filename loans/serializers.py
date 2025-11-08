"""
Serializers for Loans app.
"""

from rest_framework import serializers

from books.serializers import BookListSerializer
from loans.models import Loan
from users.serializers import LibraryUserListSerializer


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model with full CRUD operations."""

    class Meta:
        model = Loan
        fields = [
            'id',
            'book',
            'user',
            'loan_date',
            'due_date',
            'return_date',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate loan creation."""
        book = data.get('book')
        user = data.get('user')

        # Check if book is available
        if book and not self.instance:  # Only on creation
            if not book.is_available():
                raise serializers.ValidationError(
                    {'book': 'This book is not available for loan'}
                )

        # Check if user can borrow
        if user and not user.can_borrow():
            raise serializers.ValidationError(
                {'user': 'This user is not active and cannot borrow books'}
            )

        return data

    def create(self, validated_data):
        """Create loan and reserve book copy."""
        book = validated_data['book']
        loan = super().create(validated_data)
        book.reserve_copy()
        return loan


class LoanDetailSerializer(LoanSerializer):
    """Detailed loan serializer with nested book and user info."""

    book = BookListSerializer(read_only=True)
    user = LibraryUserListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True, source='book.id')
    user_id = serializers.IntegerField(write_only=True, source='user.id')
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)


class LoanBulkUploadSerializer(serializers.Serializer):
    """Serializer for bulk loan upload via file."""

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

        if value.size > 10485760:
            raise serializers.ValidationError('File size cannot exceed 10MB')

        return value
