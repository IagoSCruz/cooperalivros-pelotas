# Guia Completo de Autenticação

## Como Funciona a Autenticação JWT na API

### O que é JWT (JSON Web Token)?

JWT é um padrão de autenticação stateless (sem estado) que funciona assim:

1. **Usuário faz login** → Envia username/password
2. **Servidor valida** → Se correto, gera um token JWT
3. **Cliente armazena** → Guarda o token (localStorage, cookies, etc)
4. **Cliente usa token** → Envia em cada requisição no header
5. **Servidor valida token** → Verifica se é válido e autoriza a ação

### Diferença entre User do Django e LibraryUser

**IMPORTANTE:** São dois tipos de usuários diferentes:

#### 1. **Django User** (Autenticação - Sistema)
- **Propósito**: Autenticação na API e Admin
- **Onde**: Tabela `auth_user` do Django
- **Quem**: Administradores, bibliotecários, staff
- **Acessa**: API, painel administrativo
- **Como criar**: Via `createsuperuser` ou admin

#### 2. **LibraryUser** (Dados - Negócio)
- **Propósito**: Usuários da biblioteca (quem pega livros emprestados)
- **Onde**: Tabela `users_libraryuser` (nossa model)
- **Quem**: Leitores, pessoas que pegam livros emprestados
- **Acessa**: Apenas registro de empréstimos
- **Como criar**: Via API ou admin (cadastro de leitores)

---

## Fluxo Completo de Autenticação

### Etapa 1: Criar Usuário do Sistema (Django User)

**Opção A: Via comando (recomendado para primeiro admin)**
```bash
poetry run python manage.py createsuperuser

# Vai pedir:
# Username: admin
# Email: admin@example.com
# Password: (digite sua senha)
# Password (again): (confirme)
```

**Opção B: Via Django Admin**
1. Acesse: `http://localhost:8000/admin/`
2. Login com superuser
3. Vá em "Users" → "Add User"
4. Preencha username e password
5. Configure permissões (staff, superuser, etc)

**Opção C: Via Python/Django Shell**
```bash
poetry run python manage.py shell
```
```python
from django.contrib.auth.models import User

# Criar superuser
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='senha_segura_123'
)

# Criar user normal (sem acesso ao admin)
User.objects.create_user(
    username='bibliotecario',
    email='bib@example.com',
    password='senha123'
)
```

### Etapa 2: Obter Token JWT

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "senha_segura_123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1OTQ1MjAwLCJpYXQiOjE3MzU5NDE2MDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjF9.signature",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNjAyODAwMCwiaWF0IjoxNzM1OTQxNjAwLCJqdGkiOiJ4eXo0NTYiLCJ1c2VyX2lkIjoxfQ.signature"
}
```

**O que você recebe:**
- **access**: Token de acesso (válido por 1 hora)
- **refresh**: Token de renovação (válido por 7 dias)

### Etapa 3: Usar o Token nas Requisições

**Exemplo: Criar um livro**
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "isbn": "9780451524935",
    "quantity": 2
  }'
```

**IMPORTANTE:**
- Sempre adicione o header: `Authorization: Bearer {seu_access_token}`
- Use o token **access**, não o refresh

### Etapa 4: Renovar o Token (quando expirar)

Quando o access token expirar (após 1 hora), use o refresh token:

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Response:**
```json
{
  "access": "novo_access_token_aqui...",
  "refresh": "novo_refresh_token_aqui..."
}
```

Agora use o novo access token nas próximas requisições.

---

## Configuração Atual da API

### Permissões (settings.py)

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

**O que isso significa:**
- ✅ **Leitura (GET)**: Qualquer um pode fazer (sem autenticação)
- 🔒 **Escrita (POST/PUT/PATCH/DELETE)**: Precisa estar autenticado

### Endpoints Públicos vs Protegidos

#### ✅ Públicos (sem autenticação necessária)
```
GET /api/books/              # Listar livros
GET /api/books/{id}/         # Ver detalhes de um livro
GET /api/books/available/    # Ver livros disponíveis
GET /api/users/              # Listar usuários
GET /api/loans/              # Listar empréstimos
```

#### 🔒 Protegidos (requer autenticação)
```
POST   /api/books/                    # Criar livro
PUT    /api/books/{id}/               # Atualizar livro
PATCH  /api/books/{id}/               # Atualizar parcial
DELETE /api/books/{id}/               # Deletar livro
POST   /api/books/bulk_upload/        # Upload em massa
POST   /api/users/                    # Criar usuário da biblioteca
POST   /api/loans/                    # Criar empréstimo
POST   /api/loans/{id}/return_loan/   # Marcar como devolvido
```

---

## Exemplos Práticos Completos

### Cenário 1: Setup Inicial do Sistema

```bash
# 1. Criar primeiro administrador
poetry run python manage.py createsuperuser
# Username: admin
# Password: admin123

# 2. Iniciar servidor
poetry run python manage.py runserver

# 3. Obter token JWT
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Copie o access token da resposta
```

### Cenário 2: Bibliotecário Cadastrando Livros

```bash
# Token obtido anteriormente
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Criar livro individual
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Dom Casmurro",
    "author": "Machado de Assis",
    "isbn": "9788535908770",
    "publisher": "Cia das Letras",
    "publication_year": 1899,
    "category": "Romance",
    "quantity": 5
  }'

# Upload em massa via arquivo
curl -X POST http://localhost:8000/api/books/bulk_upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@examples/books_example.txt" \
  -F "file_type=txt"
```

### Cenário 3: Cadastrar Leitor da Biblioteca

```bash
TOKEN="seu_token_aqui"

# Criar um LibraryUser (leitor)
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "full_name": "Maria Silva",
    "email": "maria.silva@example.com",
    "phone": "11987654321",
    "address": "Rua das Flores, 123",
    "registration_number": "LEI001",
    "is_active": true
  }'
```

### Cenário 4: Fazer um Empréstimo

```bash
TOKEN="seu_token_aqui"

# Criar empréstimo
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "book": 1,
    "user": 1,
    "loan_date": "2025-01-04"
  }'

# Marcar como devolvido
curl -X POST http://localhost:8000/api/loans/1/return_loan/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testando Autenticação na Interface Swagger

1. **Acesse**: http://localhost:8000/api/docs/

2. **Obter Token**:
   - Vá em `/api/auth/token/`
   - Clique em "Try it out"
   - Preencha username e password
   - Execute
   - Copie o `access` token

3. **Autorizar**:
   - Clique no botão "Authorize" (🔓) no topo da página
   - Digite: `Bearer seu_access_token_aqui`
   - Clique em "Authorize"
   - Agora você está autenticado!

4. **Testar Endpoints Protegidos**:
   - Experimente criar um livro em `/api/books/`
   - Faça upload de arquivo em `/api/books/bulk_upload/`

---

## Estrutura do Token JWT

Um token JWT tem 3 partes separadas por `.`:

```
header.payload.signature
```

**Exemplo decodificado:**
```json
{
  "token_type": "access",
  "exp": 1735945200,        // Expira em (timestamp Unix)
  "iat": 1735941600,        // Emitido em (timestamp Unix)
  "jti": "abc123",          // ID único do token
  "user_id": 1              // ID do usuário
}
```

**Vantagens do JWT:**
- ✅ Stateless (servidor não precisa guardar sessão)
- ✅ Escalável (funciona bem com múltiplos servidores)
- ✅ Seguro (assinado criptograficamente)
- ✅ Portátil (funciona em diferentes plataformas)

---

## Segurança: Boas Práticas

### ✅ Faça

1. **Use HTTPS em produção**
   ```python
   # Em produção (settings.py)
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Guarde o token com segurança**
   - Frontend: httpOnly cookies (melhor) ou localStorage
   - Mobile: Secure storage (Keychain/KeyStore)

3. **Implemente refresh automático**
   ```javascript
   // Exemplo JavaScript
   async function refreshToken() {
     const response = await fetch('/api/auth/token/refresh/', {
       method: 'POST',
       body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
     });
     const data = await response.json();
     localStorage.setItem('access_token', data.access);
   }
   ```

4. **Configure tempo de expiração apropriado**
   ```python
   # config/settings.py
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),   # Curto
       'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Mais longo
   }
   ```

### ❌ Não Faça

- ❌ Armazenar senha em texto puro
- ❌ Compartilhar tokens entre usuários
- ❌ Enviar tokens via URL (query params)
- ❌ Usar tokens expirados
- ❌ Desabilitar HTTPS em produção

---

## Troubleshooting

### Erro: "Authentication credentials were not provided"
**Solução**: Adicione o header Authorization com o token

### Erro: "Given token not valid for any token type"
**Solução**: Token expirado ou inválido. Obtenha um novo token

### Erro: "User is inactive"
**Solução**: Ative o usuário no admin Django

### Como ver se token é válido?
```python
# Django shell
from rest_framework_simplejwt.tokens import AccessToken

token = "seu_token_aqui"
try:
    AccessToken(token)
    print("Token válido!")
except Exception as e:
    print(f"Token inválido: {e}")
```

---

## Resumo: Checklist de Uso

- [ ] Criar usuário Django (superuser ou staff)
- [ ] Obter token JWT via `/api/auth/token/`
- [ ] Guardar access e refresh tokens
- [ ] Usar access token no header: `Authorization: Bearer {token}`
- [ ] Renovar com refresh token quando expirar
- [ ] LibraryUser é diferente - são os leitores da biblioteca

---

## Próximos Passos

Se quiser customizar mais a autenticação:

1. **Adicionar permissões granulares**
2. **Implementar roles (admin, bibliotecário, etc)**
3. **Adicionar autenticação social (Google, Facebook)**
4. **Implementar 2FA (autenticação de dois fatores)**
5. **Criar endpoint de registro de usuários**

Quer que eu implemente alguma dessas funcionalidades?
