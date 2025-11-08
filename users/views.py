"""
Views for Users app.
Provides REST API endpoints for library user management.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import LibraryUser
from users.repositories import UserRepository
from users.serializers import (
    LibraryUserBulkUploadSerializer,
    LibraryUserListSerializer,
    LibraryUserSerializer,
)
from users.utils import UserFileProcessor


@extend_schema_view(
    list=extend_schema(summary='List all library users', tags=['Users']),
    retrieve=extend_schema(summary='Get user details', tags=['Users']),
    create=extend_schema(summary='Create a new user', tags=['Users']),
    update=extend_schema(summary='Update a user', tags=['Users']),
    partial_update=extend_schema(summary='Partially update a user', tags=['Users']),
    destroy=extend_schema(summary='Delete a user', tags=['Users']),
)
class LibraryUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing library users.

    Provides CRUD operations and bulk upload functionality.
    """

    queryset = LibraryUser.objects.all()
    serializer_class = LibraryUserSerializer
    search_fields = ['full_name', 'email', 'registration_number']
    ordering_fields = ['full_name', 'created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return LibraryUserListSerializer
        if self.action == 'bulk_upload':
            return LibraryUserBulkUploadSerializer
        return LibraryUserSerializer

    @extend_schema(
        summary='List active users',
        description='Returns users who can borrow books',
        tags=['Users'],
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active users."""
        users = UserRepository.get_active_users()
        serializer = LibraryUserListSerializer(users, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Bulk upload users',
        description="""
        Upload multiple users from a TXT or Excel file.

        **TXT Format (pipe-delimited):**
        ```
        full_name|email|phone|address|registration_number|is_active
        John Doe|john@example.com|1234567890|123 Main St|REG001|True
        Jane Smith|jane@example.com|0987654321|456 Oak Ave|REG002|True
        ```

        **Excel Format:**
        Columns: full_name, email, phone, address, registration_number, is_active
        """,
        tags=['Users'],
    )
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload users from TXT or Excel file."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        file_type = serializer.validated_data['file_type']

        result = UserFileProcessor.process_file(file, file_type)

        if result['success']:
            return Response(
                {
                    'message': f'Successfully imported {result["created"]} users',
                    'created': result['created'],
                    'errors': result['errors'],
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    'message': 'Failed to import users',
                    'created': result['created'],
                    'errors': result['errors'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
