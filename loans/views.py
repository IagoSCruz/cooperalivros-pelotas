"""
Views for Loans app.
Provides REST API endpoints for loan management.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from loans.models import Loan
from loans.repositories import LoanRepository
from loans.serializers import LoanDetailSerializer, LoanSerializer


@extend_schema_view(
    list=extend_schema(summary='List all loans', tags=['Loans']),
    retrieve=extend_schema(summary='Get loan details', tags=['Loans']),
    create=extend_schema(summary='Create a new loan', tags=['Loans']),
    update=extend_schema(summary='Update a loan', tags=['Loans']),
    partial_update=extend_schema(summary='Partially update a loan', tags=['Loans']),
    destroy=extend_schema(summary='Delete a loan', tags=['Loans']),
)
class LoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book loans.

    Provides CRUD operations and loan-specific actions.
    """

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    search_fields = ['book__title', 'user__full_name', 'user__registration_number']
    ordering_fields = ['loan_date', 'due_date', 'created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['retrieve', 'list']:
            return LoanDetailSerializer
        return LoanSerializer

    @extend_schema(
        summary='List active loans',
        description='Returns all loans that have not been returned',
        tags=['Loans'],
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active loans."""
        loans = LoanRepository.get_active_loans()
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='List overdue loans',
        description='Returns all loans that are past their due date',
        tags=['Loans'],
    )
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue loans."""
        loans = LoanRepository.get_overdue_loans()
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Mark loan as returned',
        description='Mark a loan as returned and update book availability',
        tags=['Loans'],
    )
    @action(detail=True, methods=['post'])
    def return_loan(self, request, pk=None):
        """Mark a loan as returned."""
        loan = self.get_object()

        if loan.status == Loan.LoanStatus.RETURNED:
            return Response(
                {'message': 'This loan has already been returned'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan.mark_as_returned()

        return Response(
            {
                'message': 'Loan marked as returned successfully',
                'loan': LoanDetailSerializer(loan).data,
            },
            status=status.HTTP_200_OK,
        )
