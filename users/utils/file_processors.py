"""
File processors for importing library users from TXT and Excel files.
"""

import pandas as pd
from django.db import transaction

from users.models import LibraryUser


class UserFileProcessor:
    """
    Processor for importing library users from different file formats.

    TXT Format Example:
    full_name|email|phone|address|registration_number|is_active
    John Doe|john@example.com|1234567890|123 Main St|REG001|True

    Excel Format:
    Columns: full_name, email, phone, address, registration_number, is_active
    """

    @staticmethod
    def process_txt_file(file) -> dict:
        """Process TXT file with pipe-delimited format."""
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return {
                'success': False,
                'created': 0,
                'errors': ['File must contain at least a header and one data row'],
            }

        header = lines[0].strip().split('|')
        expected_fields = [
            'full_name',
            'email',
            'phone',
            'address',
            'registration_number',
            'is_active',
        ]

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

                    data = {
                        'full_name': fields[0].strip(),
                        'email': fields[1].strip(),
                        'phone': fields[2].strip(),
                        'address': fields[3].strip(),
                        'registration_number': fields[4].strip(),
                        'is_active': fields[5].strip().lower() in [
                            'true',
                            '1',
                            'yes',
                        ],
                    }

                    if LibraryUser.objects.filter(
                        registration_number=data['registration_number']
                    ).exists():
                        errors.append(
                            f'Line {idx}: User with registration {data["registration_number"]} already exists'
                        )
                        continue

                    if LibraryUser.objects.filter(email=data['email']).exists():
                        errors.append(
                            f'Line {idx}: User with email {data["email"]} already exists'
                        )
                        continue

                    LibraryUser.objects.create(**data)
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
        """Process Excel file (.xlsx or .xls)."""
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return {
                'success': False,
                'created': 0,
                'errors': [f'Error reading Excel file: {e!s}'],
            }

        expected_columns = [
            'full_name',
            'email',
            'phone',
            'address',
            'registration_number',
            'is_active',
        ]

        df.columns = df.columns.str.lower().str.strip()

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
                    if pd.isna(row['full_name']) or pd.isna(
                        row['registration_number']
                    ):
                        continue

                    data = {
                        'full_name': str(row['full_name']).strip(),
                        'email': str(row['email']).strip(),
                        'phone': (
                            str(row['phone']).strip() if pd.notna(row['phone']) else ''
                        ),
                        'address': (
                            str(row['address']).strip()
                            if pd.notna(row['address'])
                            else ''
                        ),
                        'registration_number': str(row['registration_number']).strip(),
                        'is_active': bool(row['is_active'])
                        if pd.notna(row['is_active'])
                        else True,
                    }

                    if LibraryUser.objects.filter(
                        registration_number=data['registration_number']
                    ).exists():
                        errors.append(
                            f'Row {idx + 2}: User with registration {data["registration_number"]} already exists'
                        )
                        continue

                    if LibraryUser.objects.filter(email=data['email']).exists():
                        errors.append(
                            f'Row {idx + 2}: User with email {data["email"]} already exists'
                        )
                        continue

                    LibraryUser.objects.create(**data)
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
        """Process file based on type."""
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
