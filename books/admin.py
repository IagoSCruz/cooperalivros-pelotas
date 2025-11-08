"""Django admin configuration for books app."""

from django.contrib import admin

from books.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""

    list_display = [
        'title',
        'author',
        'isbn',
        'category',
        'quantity',
        'available_quantity',
        'created_at',
    ]
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            'Book Information',
            {
                'fields': (
                    'title',
                    'author',
                    'isbn',
                    'publisher',
                    'publication_year',
                    'category',
                )
            },
        ),
        (
            'Availability',
            {'fields': ('quantity', 'available_quantity')},
        ),
        (
            'Timestamps',
            {'fields': ('created_at', 'updated_at')},
        ),
    )
    ordering = ['title']
