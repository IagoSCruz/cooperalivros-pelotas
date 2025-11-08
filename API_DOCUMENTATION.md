# API Documentation

Documentação completa da API RESTful do Sistema de Gestão Bibliotecária.

## Base URL

```
http://localhost:8000/api/
```

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação.

### Obter Token

```bash
POST /api/auth/token/
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token

Inclua o token no header das requisições:

```
Authorization: Bearer {access_token}
```

### Renovar Token

```bash
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Endpoints

### Books (Livros)

#### Listar Livros
```
GET /api/books/
```

**Query Parameters:**
- `search`: Buscar por título, autor ou ISBN
- `ordering`: Ordenar por campo (title, author, created_at)
- `page`: Número da página

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "author": "F. Scott Fitzgerald",
      "isbn": "9780743273565",
      "category": "Fiction",
      "available_quantity": 3,
      "is_available": true
    }
  ]
}
```

#### Criar Livro
```
POST /api/books/
```

**Request Body:**
```json
{
  "title": "1984",
  "author": "George Orwell",
  "isbn": "9780451524935",
  "publisher": "Signet Classic",
  "publication_year": 1949,
  "category": "Fiction",
  "quantity": 2
}
```

#### Buscar Livros Disponíveis
```
GET /api/books/available/
```

#### Upload em Massa (TXT)
```
POST /api/books/bulk_upload/
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Arquivo .txt
- `file_type`: "txt"

**TXT Format:**
```
title|author|isbn|publisher|publication_year|category|quantity
The Great Gatsby|F. Scott Fitzgerald|9780743273565|Scribner|1925|Fiction|3
1984|George Orwell|9780451524935|Signet Classic|1949|Fiction|2
```

**Response:**
```json
{
  "message": "Successfully imported 2 books",
  "created": 2,
  "errors": []
}
```

#### Upload em Massa (Excel)
```
POST /api/books/bulk_upload/
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Arquivo .xlsx ou .xls
- `file_type`: "excel"

**Excel Columns:**
- title
- author
- isbn
- publisher
- publication_year
- category
- quantity

---

### Users (Usuários)

#### Listar Usuários
```
GET /api/users/
```

**Query Parameters:**
- `search`: Buscar por nome, email ou número de registro
- `ordering`: Ordenar por campo
- `page`: Número da página

#### Criar Usuário
```
POST /api/users/
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "address": "123 Main St",
  "registration_number": "REG001",
  "is_active": true
}
```

#### Buscar Usuários Ativos
```
GET /api/users/active/
```

#### Upload em Massa (TXT)
```
POST /api/users/bulk_upload/
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Arquivo .txt
- `file_type`: "txt"

**TXT Format:**
```
full_name|email|phone|address|registration_number|is_active
John Doe|john@example.com|1234567890|123 Main St|REG001|True
Jane Smith|jane@example.com|0987654321|456 Oak Ave|REG002|True
```

---

### Loans (Empréstimos)

#### Listar Empréstimos
```
GET /api/loans/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "book": {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald"
      },
      "user": {
        "id": 1,
        "full_name": "John Doe",
        "registration_number": "REG001"
      },
      "loan_date": "2025-01-01",
      "due_date": "2025-01-15",
      "return_date": null,
      "status": "active",
      "is_overdue": false,
      "days_overdue": 0
    }
  ]
}
```

#### Criar Empréstimo
```
POST /api/loans/
```

**Request Body:**
```json
{
  "book": 1,
  "user": 1,
  "loan_date": "2025-01-01",
  "due_date": "2025-01-15",
  "notes": "Optional notes"
}
```

**Nota:** Se `due_date` não for fornecido, será automaticamente definido para 14 dias após `loan_date`.

#### Buscar Empréstimos Ativos
```
GET /api/loans/active/
```

#### Buscar Empréstimos Atrasados
```
GET /api/loans/overdue/
```

#### Marcar como Devolvido
```
POST /api/loans/{id}/return_loan/
```

**Response:**
```json
{
  "message": "Loan marked as returned successfully",
  "loan": {
    "id": 1,
    "return_date": "2025-01-10",
    "status": "returned"
  }
}
```

---

## Validações

### Books
- ISBN deve ter 10 ou 13 dígitos
- ISBN deve ser único
- `quantity` deve ser >= `available_quantity`
- `available_quantity` >= 0

### Users
- Email deve ser único e válido
- `registration_number` deve ser único

### Loans
- Livro deve estar disponível (`available_quantity` > 0)
- Usuário deve estar ativo (`is_active` = true)
- Ao criar empréstimo, uma cópia do livro é automaticamente reservada
- Ao marcar como devolvido, a cópia é automaticamente liberada

---

## Códigos de Status HTTP

- `200 OK`: Sucesso
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Sem permissão
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro no servidor

---

## Paginação

Por padrão, a API retorna 20 itens por página. Use os parâmetros:
- `page`: Número da página
- `page_size`: Itens por página (máximo 100)

Exemplo:
```
GET /api/books/?page=2&page_size=50
```

---

## Busca e Filtros

Use o parâmetro `search` para busca textual:
```
GET /api/books/?search=gatsby
GET /api/users/?search=john@example.com
```

Use `ordering` para ordenação:
```
GET /api/books/?ordering=title
GET /api/books/?ordering=-created_at  # Ordem decrescente
```

---

## Exemplos com cURL

### Criar Livro
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "isbn": "9780451524935",
    "quantity": 2
  }'
```

### Upload em Massa (TXT)
```bash
curl -X POST http://localhost:8000/api/books/bulk_upload/ \
  -F "file=@examples/books_example.txt" \
  -F "file_type=txt"
```

### Criar Empréstimo
```bash
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "book": 1,
    "user": 1,
    "loan_date": "2025-01-01"
  }'
```

### Marcar Empréstimo como Devolvido
```bash
curl -X POST http://localhost:8000/api/loans/1/return_loan/ \
  -H "Authorization: Bearer {token}"
```

---

## Interface Interativa

Para explorar a API interativamente, acesse:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

A documentação interativa permite:
- Testar todos os endpoints diretamente no navegador
- Ver exemplos de request/response
- Gerar código de cliente em várias linguagens
- Validar schemas automaticamente
