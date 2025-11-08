"""
Views for the frontend application.
Serves HTML templates for the web interface.
"""

from django.shortcuts import render


def index(request):
    """Render the main catalog page."""
    return render(request, 'index.html')


def add_book(request):
    """Render the add book page."""
    return render(request, 'add_book.html')


def login(request):
    """Render the login page."""
    return render(request, 'login.html')
