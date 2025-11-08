"""
URL configuration for frontend application.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-book', views.add_book, name='add_book'),
    path('login', views.login, name='login'),
]
