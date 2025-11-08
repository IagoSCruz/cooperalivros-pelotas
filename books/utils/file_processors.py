"""
File processors for importing books from TXT and Excel files.
Supports legacy data migration from text-based records.
"""

import pandas as pd
from django.db import transaction

from books.models import Book


class BookFileProcessor:
    """
    Processor for importing books from different file formats.

    Supported formats:
    - TXT: Pipe-delimited format (|)
    - Excel: .xlsx or .xls files

    TXT Format Example:
    title|author|isbn|publisher|publication_year|category|quantity
    The Great Gatsby|F. Scott Fitzgerald|9780743273565|Scribner|1925|Fiction|3

    Excel Format:
    Columns: title, author, isbn, publisher, publication_year, category, quantity
    """

    @staticmethod
    def process_txt_file(file) -> dict:
        """
        Process TXT file with pipe-delimited format.

        Args:
            file: Uploaded file object

        Returns:
            dict with 'success', 'created', 'errors' keys
        """
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return {
                'success': False,
                'created': 0,
                'errors': ['File must contain at least a header and one data row'],
            }

        # Parse header
        header = lines[0].strip().split('|')
        expected_fields = [
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_year',
            'category',
            'quantity',
        ]

        # Validate header
        if header != expected_fields:
            return {
                'success': False,
                'created': 0,
                'errors': [
                    f'Invalid header. Expected: {"|".join(expected_fields)}'
                ],
            }

        created_count = 0
        errors = []

        with transaction.atomic():
            for idx, line in enumerate(lines[1:], start=2):
                if not line.strip():
                    continue

                try:
                    fields = line.strip().split('|')
                    if len(fields) != len(expected_fields):
                        errors.append(
                            f'Line {idx}: Expected {len(expected_fields)} fields, got {len(fields)}'
                        )
                        continue

                    # Parse data
                    data = {
                        'title': fields[0].strip(),
                        'author': fields[1].strip(),
                        'isbn': fields[2].strip(),
                        'publisher': fields[3].strip(),
                        'publication_year': (
                            int(fields[4].strip()) if fields[4].strip() else None
                        ),
                        'category': fields[5].strip(),
                        'quantity': int(fields[6].strip()),
                        'available_quantity': int(fields[6].strip()),
                    }

                    # Check if book with same ISBN already exists
                    if Book.objects.filter(isbn=data['isbn']).exists():
                        errors.append(
                            f'Line {idx}: Book with ISBN {data["isbn"]} already exists'
                        )
                        continue

                    Book.objects.create(**data)
                    created_count += 1

                except (ValueError, IndexError) as e:
                    errors.append(f'Line {idx}: {e!s}')

        return {
            'success': created_count > 0,
            'created': created_count,
            'errors': errors,
        }

    @staticmethod
    def process_excel_file(file) -> dict:
        """
        Process Excel file (.xlsx or .xls).

        Args:
            file: Uploaded file object

        Returns:
            dict with 'success', 'created', 'errors' keys
        """
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return {
                'success': False,
                'created': 0,
                'errors': [f'Error reading Excel file: {e!s}'],
            }

        expected_columns = [
            'title',
            'author',
            'isbn',
            'publisher',
            'publication_year',
            'category',
            'quantity',
        ]

        # Normalize column names (lowercase, strip whitespace)
        df.columns = df.columns.str.lower().str.strip()

        # Validate columns
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            return {
                'success': False,
                'created': 0,
                'errors': [f'Missing required columns: {", ".join(missing_columns)}'],
            }

        created_count = 0
        errors = []

        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row['title']) or pd.isna(row['isbn']):
                        continue

                    data = {
                        'title': str(row['title']).strip(),
                        'author': str(row['author']).strip(),
                        'isbn': str(row['isbn']).strip(),
                        'publisher': (
                            str(row['publisher']).strip()
                            if pd.notna(row['publisher'])
                            else ''
                        ),
                        'publication_year': (
                            int(row['publication_year'])
                            if pd.notna(row['publication_year'])
                            else None
                        ),
                        'category': (
                            str(row['category']).strip()
                            if pd.notna(row['category'])
                            else ''
                        ),
                        'quantity': int(row['quantity']),
                        'available_quantity': int(row['quantity']),
                    }

                    # Check if book with same ISBN already exists
                    if Book.objects.filter(isbn=data['isbn']).exists():
                        errors.append(
                            f'Row {idx + 2}: Book with ISBN {data["isbn"]} already exists'
                        )
                        continue

                    Book.objects.create(**data)
                    created_count += 1

                except (ValueError, KeyError) as e:
                    errors.append(f'Row {idx + 2}: {e!s}')

        return {
            'success': created_count > 0,
            'created': created_count,
            'errors': errors,
        }

    @classmethod
    def process_file(cls, file, file_type: str) -> dict:
        """
        Process file based on type.

        Args:
            file: Uploaded file object
            file_type: Type of file ('txt' or 'excel')

        Returns:
            dict with processing results
        """
        if file_type == 'txt':
            return cls.process_txt_file(file)
        elif file_type == 'excel':
            return cls.process_excel_file(file)
        else:
            return {
                'success': False,
                'created': 0,
                'errors': [f'Unsupported file type: {file_type}'],
            }
