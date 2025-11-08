"""
Exemplo de cliente Python para consumir a API do Sistema de Gestão Bibliotecária.

Este script demonstra como autenticar e usar todos os endpoints da API.
"""

import requests
from datetime import datetime


class LibraryAPIClient:
    """Cliente para interagir com a API da Biblioteca."""

    def __init__(self, base_url='http://localhost:8000'):
        """
        Inicializa o cliente da API.

        Args:
            base_url: URL base da API (padrão: http://localhost:8000)
        """
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None

    def login(self, username: str, password: str) -> dict:
        """
        Faz login e obtém tokens JWT.

        Args:
            username: Nome de usuário
            password: Senha

        Returns:
            dict com access e refresh tokens
        """
        url = f'{self.base_url}/api/auth/token/'
        data = {'username': username, 'password': password}

        response = requests.post(url, json=data)
        response.raise_for_status()

        tokens = response.json()
        self.access_token = tokens['access']
        self.refresh_token = tokens['refresh']

        print(f'✅ Login realizado com sucesso!')
        print(f'Access Token: {self.access_token[:50]}...')
        return tokens

    def refresh_access_token(self) -> dict:
        """
        Renova o access token usando o refresh token.

        Returns:
            dict com novo access e refresh tokens
        """
        url = f'{self.base_url}/api/auth/token/refresh/'
        data = {'refresh': self.refresh_token}

        response = requests.post(url, json=data)
        response.raise_for_status()

        tokens = response.json()
        self.access_token = tokens['access']
        self.refresh_token = tokens.get('refresh', self.refresh_token)

        print('✅ Token renovado com sucesso!')
        return tokens

    def _get_headers(self) -> dict:
        """Retorna headers com autenticação."""
        if not self.access_token:
            raise ValueError('Você precisa fazer login primeiro!')

        return {'Authorization': f'Bearer {self.access_token}'}

    # ==================== BOOKS ====================

    def list_books(self, search: str = None, page: int = 1) -> dict:
        """
        Lista todos os livros.

        Args:
            search: Termo de busca (opcional)
            page: Número da página

        Returns:
            dict com lista de livros
        """
        url = f'{self.base_url}/api/books/'
        params = {'page': page}
        if search:
            params['search'] = search

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_book(self, book_id: int) -> dict:
        """Obtém detalhes de um livro."""
        url = f'{self.base_url}/api/books/{book_id}/'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def create_book(self, book_data: dict) -> dict:
        """
        Cria um novo livro.

        Args:
            book_data: Dados do livro
                - title (str): Título
                - author (str): Autor
                - isbn (str): ISBN
                - publisher (str, opcional): Editora
                - publication_year (int, opcional): Ano
                - category (str, opcional): Categoria
                - quantity (int): Quantidade total

        Returns:
            dict com dados do livro criado
        """
        url = f'{self.base_url}/api/books/'
        headers = self._get_headers()

        response = requests.post(url, json=book_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def update_book(self, book_id: int, book_data: dict) -> dict:
        """Atualiza um livro completamente."""
        url = f'{self.base_url}/api/books/{book_id}/'
        headers = self._get_headers()

        response = requests.put(url, json=book_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def partial_update_book(self, book_id: int, book_data: dict) -> dict:
        """Atualiza parcialmente um livro."""
        url = f'{self.base_url}/api/books/{book_id}/'
        headers = self._get_headers()

        response = requests.patch(url, json=book_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete_book(self, book_id: int) -> None:
        """Deleta um livro."""
        url = f'{self.base_url}/api/books/{book_id}/'
        headers = self._get_headers()

        response = requests.delete(url, headers=headers)
        response.raise_for_status()

    def list_available_books(self) -> list:
        """Lista livros disponíveis para empréstimo."""
        url = f'{self.base_url}/api/books/available/'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def bulk_upload_books(self, file_path: str, file_type: str = 'txt') -> dict:
        """
        Upload em massa de livros via arquivo.

        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo ('txt' ou 'excel')

        Returns:
            dict com resultado do upload
        """
        url = f'{self.base_url}/api/books/bulk_upload/'
        headers = self._get_headers()

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'file_type': file_type}
            response = requests.post(url, files=files, data=data, headers=headers)

        response.raise_for_status()
        return response.json()

    # ==================== USERS ====================

    def list_users(self, search: str = None, page: int = 1) -> dict:
        """Lista todos os usuários da biblioteca."""
        url = f'{self.base_url}/api/users/'
        params = {'page': page}
        if search:
            params['search'] = search

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def create_user(self, user_data: dict) -> dict:
        """
        Cria um novo usuário da biblioteca.

        Args:
            user_data: Dados do usuário
                - full_name (str): Nome completo
                - email (str): Email
                - registration_number (str): Número de registro
                - phone (str, opcional): Telefone
                - address (str, opcional): Endereço
                - is_active (bool, opcional): Ativo (padrão: True)

        Returns:
            dict com dados do usuário criado
        """
        url = f'{self.base_url}/api/users/'
        headers = self._get_headers()

        response = requests.post(url, json=user_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def bulk_upload_users(self, file_path: str, file_type: str = 'txt') -> dict:
        """Upload em massa de usuários via arquivo."""
        url = f'{self.base_url}/api/users/bulk_upload/'
        headers = self._get_headers()

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'file_type': file_type}
            response = requests.post(url, files=files, data=data, headers=headers)

        response.raise_for_status()
        return response.json()

    # ==================== LOANS ====================

    def list_loans(self, page: int = 1) -> dict:
        """Lista todos os empréstimos."""
        url = f'{self.base_url}/api/loans/'
        params = {'page': page}

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def create_loan(self, book_id: int, user_id: int, loan_date: str = None) -> dict:
        """
        Cria um novo empréstimo.

        Args:
            book_id: ID do livro
            user_id: ID do usuário
            loan_date: Data do empréstimo (formato: YYYY-MM-DD)
                      Se não fornecido, usa data atual

        Returns:
            dict com dados do empréstimo criado
        """
        url = f'{self.base_url}/api/loans/'
        headers = self._get_headers()

        data = {'book': book_id, 'user': user_id}
        if loan_date:
            data['loan_date'] = loan_date
        else:
            data['loan_date'] = datetime.now().strftime('%Y-%m-%d')

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def list_active_loans(self) -> list:
        """Lista empréstimos ativos."""
        url = f'{self.base_url}/api/loans/active/'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def list_overdue_loans(self) -> list:
        """Lista empréstimos atrasados."""
        url = f'{self.base_url}/api/loans/overdue/'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def return_loan(self, loan_id: int) -> dict:
        """
        Marca um empréstimo como devolvido.

        Args:
            loan_id: ID do empréstimo

        Returns:
            dict com dados do empréstimo atualizado
        """
        url = f'{self.base_url}/api/loans/{loan_id}/return_loan/'
        headers = self._get_headers()

        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()


# ==================== EXEMPLOS DE USO ====================


def main():
    """Exemplos de uso do cliente da API."""
    # Inicializar cliente
    client = LibraryAPIClient(base_url='http://localhost:8000')

    # 1. Login
    print('\n=== 1. AUTENTICAÇÃO ===')
    try:
        client.login(username='admin', password='admin123')
    except requests.exceptions.HTTPError as e:
        print(f'❌ Erro no login: {e}')
        print('Certifique-se de criar um superuser primeiro!')
        return

    # 2. Listar livros (não precisa autenticação)
    print('\n=== 2. LISTAR LIVROS ===')
    books = client.list_books()
    print(f'Total de livros: {books["count"]}')
    if books['results']:
        print(f'Primeiro livro: {books["results"][0]}')

    # 3. Criar um livro (precisa autenticação)
    print('\n=== 3. CRIAR LIVRO ===')
    new_book = {
        'title': 'Dom Casmurro',
        'author': 'Machado de Assis',
        'isbn': '9788535908770',
        'publisher': 'Cia das Letras',
        'publication_year': 1899,
        'category': 'Romance',
        'quantity': 5,
    }
    try:
        created_book = client.create_book(new_book)
        print(f'✅ Livro criado: {created_book["title"]} (ID: {created_book["id"]})')
    except requests.exceptions.HTTPError as e:
        print(f'❌ Erro ao criar livro: {e.response.json()}')

    # 4. Upload em massa
    print('\n=== 4. UPLOAD EM MASSA ===')
    try:
        result = client.bulk_upload_books('examples/books_example.txt', 'txt')
        print(f'✅ {result["message"]}')
        print(f'Criados: {result["created"]}')
        if result['errors']:
            print(f'Erros: {result["errors"]}')
    except Exception as e:
        print(f'❌ Erro no upload: {e}')

    # 5. Criar usuário da biblioteca
    print('\n=== 5. CRIAR USUÁRIO DA BIBLIOTECA ===')
    new_user = {
        'full_name': 'João da Silva',
        'email': 'joao@example.com',
        'phone': '11987654321',
        'address': 'Rua das Flores, 123',
        'registration_number': 'USR999',
        'is_active': True,
    }
    try:
        created_user = client.create_user(new_user)
        print(
            f'✅ Usuário criado: {created_user["full_name"]} (ID: {created_user["id"]})'
        )
    except requests.exceptions.HTTPError as e:
        print(f'❌ Erro ao criar usuário: {e.response.json()}')

    # 6. Criar empréstimo
    print('\n=== 6. CRIAR EMPRÉSTIMO ===')
    try:
        # Usar IDs dos livros e usuários criados anteriormente
        loan = client.create_loan(book_id=1, user_id=1)
        print(f'✅ Empréstimo criado (ID: {loan["id"]})')
        print(f'Livro: {loan["book"]["title"]}')
        print(f'Usuário: {loan["user"]["full_name"]}')
        print(f'Data de devolução: {loan["due_date"]}')
    except requests.exceptions.HTTPError as e:
        print(f'❌ Erro ao criar empréstimo: {e.response.json()}')

    # 7. Listar empréstimos ativos
    print('\n=== 7. EMPRÉSTIMOS ATIVOS ===')
    active_loans = client.list_active_loans()
    print(f'Total de empréstimos ativos: {len(active_loans)}')

    # 8. Devolver empréstimo
    print('\n=== 8. DEVOLVER EMPRÉSTIMO ===')
    try:
        if active_loans:
            loan_id = active_loans[0]['id']
            result = client.return_loan(loan_id)
            print(f'✅ {result["message"]}')
    except Exception as e:
        print(f'❌ Erro ao devolver: {e}')

    print('\n=== FIM DOS EXEMPLOS ===')


if __name__ == '__main__':
    main()
