"""Django admin configuration for loans app."""

from django.contrib import admin

from loans.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin interface for Loan model."""

    list_display = [
        'book',
        'user',
        'loan_date',
        'due_date',
        'return_date',
        'status',
        'is_overdue',
    ]
    list_filter = ['status', 'loan_date', 'due_date']
    search_fields = ['book__title', 'user__full_name', 'user__registration_number']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['book', 'user']
    fieldsets = (
        (
            'Loan Information',
            {'fields': ('book', 'user')},
        ),
        (
            'Dates',
            {'fields': ('loan_date', 'due_date', 'return_date')},
        ),
        (
            'Status',
            {'fields': ('status', 'notes')},
        ),
        (
            'Timestamps',
            {'fields': ('created_at', 'updated_at')},
        ),
    )
    ordering = ['-loan_date']
    actions = ['mark_as_returned']

    def mark_as_returned(self, request, queryset):
        """Admin action to mark selected loans as returned."""
        for loan in queryset:
            loan.mark_as_returned()
        self.message_user(
            request, f'{queryset.count()} loan(s) marked as returned.'
        )

    mark_as_returned.short_description = 'Mark selected loans as returned'
