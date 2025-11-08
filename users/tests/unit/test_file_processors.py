"""
Unit tests for UserFileProcessor.
"""
import io
import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import LibraryUser
from users.utils.file_processors import UserFileProcessor


@pytest.mark.django_db
@pytest.mark.unit
class TestUserFileProcessorTXT:
    """Test suite for UserFileProcessor TXT file processing."""

    def test_process_valid_txt_file(self):
        """Test processing a valid TXT file."""
        content = """full_name|email|phone|address|registration_number|is_active
João Silva|joao@test.com|11999999999|Rua A, 123|REG001|True
Maria Santos|maria@test.com|11988888888|Rua B, 456|REG002|true"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert len(result['errors']) == 0

        # Verify users were created
        assert LibraryUser.objects.count() == 2
        user = LibraryUser.objects.get(registration_number='REG001')
        assert user.full_name == 'João Silva'
        assert user.email == 'joao@test.com'
        assert user.is_active is True

    def test_process_txt_file_with_empty_lines(self):
        """Test processing TXT file with empty lines."""
        content = """full_name|email|phone|address|registration_number|is_active
João Silva|joao@test.com|11999999999|Rua A, 123|REG001|True

Maria Santos|maria@test.com|11988888888|Rua B, 456|REG002|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert LibraryUser.objects.count() == 2

    def test_process_txt_file_invalid_header(self):
        """Test processing TXT file with invalid header."""
        content = """wrong|header|format
João Silva|joao@test.com|REG001"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'Invalid header' in result['errors'][0]

    def test_process_txt_file_insufficient_lines(self):
        """Test processing TXT file with only header."""
        content = """full_name|email|phone|address|registration_number|is_active"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert 'at least a header and one data row' in result['errors'][0]

    def test_process_txt_file_wrong_field_count(self):
        """Test processing TXT file with wrong number of fields."""
        content = """full_name|email|phone|address|registration_number|is_active
João Silva|joao@test.com|11999999999"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'Expected 6 fields' in result['errors'][0]

    def test_process_txt_file_duplicate_registration_number(self, sample_library_user):
        """Test processing TXT file with duplicate registration number."""
        content = f"""full_name|email|phone|address|registration_number|is_active
New User|new@test.com|11999999999|Street 1|{sample_library_user.registration_number}|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_txt_file_duplicate_email(self, sample_library_user):
        """Test processing TXT file with duplicate email."""
        content = f"""full_name|email|phone|address|registration_number|is_active
New User|{sample_library_user.email}|11999999999|Street 1|NEWREG|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_txt_file_is_active_true_variations(self):
        """Test is_active accepts various true values."""
        content = """full_name|email|phone|address|registration_number|is_active
User1|user1@test.com|11999999999|Street 1|REG001|True
User2|user2@test.com|11999999999|Street 2|REG002|true
User3|user3@test.com|11999999999|Street 3|REG003|1
User4|user4@test.com|11999999999|Street 4|REG004|yes"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 4

        for reg_num in ['REG001', 'REG002', 'REG003', 'REG004']:
            user = LibraryUser.objects.get(registration_number=reg_num)
            assert user.is_active is True

    def test_process_txt_file_is_active_false_values(self):
        """Test is_active treats other values as false."""
        content = """full_name|email|phone|address|registration_number|is_active
User1|user1@test.com|11999999999|Street 1|REG001|False
User2|user2@test.com|11999999999|Street 2|REG002|0
User3|user3@test.com|11999999999|Street 3|REG003|no"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 3

        for reg_num in ['REG001', 'REG002', 'REG003']:
            user = LibraryUser.objects.get(registration_number=reg_num)
            assert user.is_active is False

    def test_process_txt_file_empty_optional_fields(self):
        """Test processing TXT file with empty optional fields."""
        content = """full_name|email|phone|address|registration_number|is_active
Test User|test@test.com|||REG001|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_txt_file(file)

        assert result['success'] is True
        assert result['created'] == 1

        user = LibraryUser.objects.get(registration_number='REG001')
        assert user.phone == ''
        assert user.address == ''


@pytest.mark.django_db
@pytest.mark.unit
class TestUserFileProcessorExcel:
    """Test suite for UserFileProcessor Excel file processing."""

    def create_excel_file(self, data_rows):
        """Helper to create Excel file from data rows."""
        df = pd.DataFrame(data_rows)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return SimpleUploadedFile("users.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def test_process_valid_excel_file(self):
        """Test processing a valid Excel file."""
        data = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                'phone': '11999999999',
                'address': 'Rua A, 123',
                'registration_number': 'REG001',
                'is_active': True
            },
            {
                'full_name': 'Maria Santos',
                'email': 'maria@test.com',
                'phone': '11988888888',
                'address': 'Rua B, 456',
                'registration_number': 'REG002',
                'is_active': True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 2
        assert len(result['errors']) == 0

        assert LibraryUser.objects.count() == 2
        user = LibraryUser.objects.get(registration_number='REG001')
        assert user.full_name == 'João Silva'
        assert user.email == 'joao@test.com'

    def test_process_excel_file_missing_columns(self):
        """Test processing Excel file with missing required columns."""
        data = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                # Missing other required fields
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is False
        assert result['created'] == 0
        assert 'Missing required columns' in result['errors'][0]

    def test_process_excel_file_with_extra_columns(self):
        """Test processing Excel file with extra columns is OK."""
        data = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                'phone': '11999999999',
                'address': 'Rua A, 123',
                'registration_number': 'REG001',
                'is_active': True,
                'extra_column': 'This should be ignored'
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_excel_file_case_insensitive_columns(self):
        """Test that column names are case insensitive."""
        data = [
            {
                'FULL_NAME': 'João Silva',
                'EMAIL': 'joao@test.com',
                'PHONE': '11999999999',
                'ADDRESS': 'Rua A, 123',
                'REGISTRATION_NUMBER': 'REG001',
                'IS_ACTIVE': True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_excel_file_skip_empty_rows(self):
        """Test that empty rows are skipped."""
        data = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                'phone': '11999999999',
                'address': 'Rua A, 123',
                'registration_number': 'REG001',
                'is_active': True
            },
            {
                'full_name': None,
                'email': None,
                'phone': None,
                'address': None,
                'registration_number': None,
                'is_active': None
            },
            {
                'full_name': 'Maria Santos',
                'email': 'maria@test.com',
                'phone': '11988888888',
                'address': 'Rua B, 456',
                'registration_number': 'REG002',
                'is_active': True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 2

    def test_process_excel_file_duplicate_registration_number(self, sample_library_user):
        """Test processing Excel file with duplicate registration number."""
        data = [
            {
                'full_name': 'New User',
                'email': 'new@test.com',
                'phone': '11999999999',
                'address': 'Street 1',
                'registration_number': sample_library_user.registration_number,
                'is_active': True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_excel_file_duplicate_email(self, sample_library_user):
        """Test processing Excel file with duplicate email."""
        data = [
            {
                'full_name': 'New User',
                'email': sample_library_user.email,
                'phone': '11999999999',
                'address': 'Street 1',
                'registration_number': 'NEWREG',
                'is_active': True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['created'] == 0
        assert len(result['errors']) > 0
        assert 'already exists' in result['errors'][0]

    def test_process_excel_file_with_nan_values(self):
        """Test processing Excel file with NaN values for optional fields."""
        data = [
            {
                'full_name': 'João Silva',
                'email': 'joao@test.com',
                'phone': None,
                'address': None,
                'registration_number': 'REG001',
                'is_active': None  # Should default to True
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 1

        user = LibraryUser.objects.get(registration_number='REG001')
        assert user.phone == ''
        assert user.address == ''
        assert user.is_active is True

    def test_process_excel_file_is_active_boolean_conversion(self):
        """Test is_active converts to boolean properly."""
        data = [
            {
                'full_name': 'Active User',
                'email': 'active@test.com',
                'phone': '',
                'address': '',
                'registration_number': 'REG001',
                'is_active': True
            },
            {
                'full_name': 'Inactive User',
                'email': 'inactive@test.com',
                'phone': '',
                'address': '',
                'registration_number': 'REG002',
                'is_active': False
            }
        ]

        file = self.create_excel_file(data)
        result = UserFileProcessor.process_excel_file(file)

        assert result['success'] is True
        assert result['created'] == 2

        active_user = LibraryUser.objects.get(registration_number='REG001')
        assert active_user.is_active is True

        inactive_user = LibraryUser.objects.get(registration_number='REG002')
        assert inactive_user.is_active is False


@pytest.mark.django_db
@pytest.mark.unit
class TestUserFileProcessorGeneral:
    """Test suite for UserFileProcessor general methods."""

    def test_process_file_txt(self):
        """Test process_file routes to TXT processor."""
        content = """full_name|email|phone|address|registration_number|is_active
João Silva|joao@test.com|11999999999|Rua A, 123|REG001|True"""

        file = SimpleUploadedFile("users.txt", content.encode('utf-8'))
        result = UserFileProcessor.process_file(file, 'txt')

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_file_excel(self):
        """Test process_file routes to Excel processor."""
        df = pd.DataFrame([{
            'full_name': 'João Silva',
            'email': 'joao@test.com',
            'phone': '11999999999',
            'address': 'Rua A, 123',
            'registration_number': 'REG001',
            'is_active': True
        }])
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        file = SimpleUploadedFile("users.xlsx", buffer.read())

        result = UserFileProcessor.process_file(file, 'excel')

        assert result['success'] is True
        assert result['created'] == 1

    def test_process_file_unsupported_type(self):
        """Test process_file rejects unsupported file types."""
        file = SimpleUploadedFile("users.pdf", b"content")
        result = UserFileProcessor.process_file(file, 'pdf')

        assert result['success'] is False
        assert result['created'] == 0
        assert 'Unsupported file type' in result['errors'][0]
