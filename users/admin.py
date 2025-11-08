"""Django admin configuration for users app."""

from django.contrib import admin

from users.models import LibraryUser


@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    """Admin interface for LibraryUser model."""

    list_display = [
        'full_name',
        'registration_number',
        'email',
        'phone',
        'is_active',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'registration_number', 'email']
    autocomplete_fields = []
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            'Personal Information',
            {'fields': ('full_name', 'email', 'phone', 'address')},
        ),
        (
            'Registration',
            {'fields': ('registration_number', 'is_active')},
        ),
        (
            'Timestamps',
            {'fields': ('created_at', 'updated_at')},
        ),
    )
    ordering = ['full_name']
