"""
Serializers for Users app.
"""

from rest_framework import serializers

from users.models import LibraryUser


class LibraryUserSerializer(serializers.ModelSerializer):
    """Serializer for LibraryUser model with full CRUD operations."""

    class Meta:
        model = LibraryUser
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'address',
            'registration_number',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_registration_number(self, value):
        """Validate registration number uniqueness."""
        if self.instance:
            # Update operation
            if (
                LibraryUser.objects.exclude(pk=self.instance.pk)
                .filter(registration_number=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    'A user with this registration number already exists'
                )
        else:
            # Create operation
            if LibraryUser.objects.filter(registration_number=value).exists():
                raise serializers.ValidationError(
                    'A user with this registration number already exists'
                )
        return value


class LibraryUserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for user listings."""

    can_borrow = serializers.BooleanField(read_only=True)

    class Meta:
        model = LibraryUser
        fields = [
            'id',
            'full_name',
            'registration_number',
            'email',
            'is_active',
            'can_borrow',
        ]


class LibraryUserBulkUploadSerializer(serializers.Serializer):
    """Serializer for bulk user upload via file."""

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
