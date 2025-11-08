# Atualizações do Sistema - Upload de Imagens e Frontend

## Novas Funcionalidades Implementadas

### 1. Upload de Imagens de Capa dos Livros

#### Backend
- **Novo campo no modelo Book**: `cover_image` (ImageField)
- **Endpoint de upload**: `POST /api/books/{id}/upload_cover/`
- **Dependência adicionada**: Pillow para processamento de imagens
- **Armazenamento**: Imagens salvas em `media/books/covers/`

#### Como Usar
```python
# Via API
import requests

url = "http://localhost:8000/api/books/1/upload_cover/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"cover_image": open("capa.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
```

#### Configurações
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 2. Frontend Web Completo

#### Páginas Implementadas

##### Catálogo (`/`)
- Grid responsivo de livros
- Busca em tempo real por título, autor ou ISBN
- Filtros: Todos / Disponíveis
- Modal com detalhes completos do livro
- Exibição de capas (quando disponível)

##### Adicionar Livro (`/add-book`)
- Formulário completo de cadastro
- Upload de imagem com preview
- Importação em massa via TXT ou Excel
- Validação client-side
- Feedback de sucesso/erro

##### Login (`/login`)
- Autenticação JWT
- Armazenamento seguro de tokens
- Renovação automática de tokens expirados
- Redirecionamento automático

#### Tecnologias do Frontend
- **HTML5** - Templates Django
- **CSS3** - Design system customizado
- **JavaScript Vanilla** - Sem frameworks
- **Fetch API** - Comunicação com backend
- **JWT** - Autenticação

#### Arquivos Criados
```
templates/
├── base.html          # Template base
├── index.html         # Catálogo
├── add_book.html      # Formulário
└── login.html         # Login

web/static/
├── css/
│   └── style.css      # Estilos globais
└── js/
    ├── auth.js        # Autenticação
    ├── catalog.js     # Catálogo
    ├── add-book.js    # Formulário
    └── login.js       # Login

frontend/              # App Django
├── views.py           # Views
└── urls.py            # URLs
```

## Configurações Adicionadas

### settings.py
```python
INSTALLED_APPS = [
    # ...
    'frontend',  # Novo app
]

TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],  # Templates globais
        # ...
    }
]

STATICFILES_DIRS = [BASE_DIR / 'web' / 'static']  # Arquivos estáticos
```

### urls.py
```python
urlpatterns = [
    # ...
    path('', include('frontend.urls')),  # Frontend routes
]
```

## Migrações

Nova migração criada:
- `books/migrations/0002_book_cover_image.py` - Adiciona campo cover_image

Para aplicar:
```bash
poetry run python manage.py migrate
```

## Dependências Adicionadas

```toml
[project.dependencies]
pillow = "^12.0.0"  # Processamento de imagens
```

## Como Testar

### 1. Aplicar Migrações
```bash
poetry run python manage.py migrate
```

### 2. Criar Superusuário (se necessário)
```bash
poetry run python manage.py createsuperuser
```

### 3. Iniciar Servidor
```bash
poetry run python manage.py runserver
```

### 4. Acessar Frontend
- Catálogo: http://localhost:8000/
- Adicionar Livro: http://localhost:8000/add-book
- Login: http://localhost:8000/login

### 5. Testar Upload de Imagem

#### Via Frontend:
1. Acesse http://localhost:8000/login
2. Faça login com suas credenciais
3. Vá para http://localhost:8000/add-book
4. Preencha o formulário
5. Selecione uma imagem (formato: JPG, PNG, GIF, WEBP)
6. Visualize o preview
7. Clique em "Salvar Livro"

#### Via API:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'

# Upload de capa
curl -X POST http://localhost:8000/api/books/1/upload_cover/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "cover_image=@/path/to/image.jpg"
```

## API Endpoints Novos

### Upload de Capa
```
POST /api/books/{id}/upload_cover/

Headers:
  Authorization: Bearer {token}
  Content-Type: multipart/form-data

Body:
  cover_image: [image file]

Response:
{
  "id": 1,
  "title": "Livro Exemplo",
  "cover_image": "http://localhost:8000/media/books/covers/image.jpg",
  ...
}
```

## Segurança

### CORS
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

### JWT
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Upload de Arquivos
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

## Próximos Passos

1. **Testes**
   - Adicionar testes para upload de imagens
   - Testes de integração do frontend
   - Testes E2E com Selenium/Playwright

2. **Melhorias de UX**
   - Modo escuro
   - Notificações toast
   - Loading states mais elaborados
   - Animações de transição

3. **Funcionalidades**
   - Página de empréstimos no frontend
   - Edição/exclusão de livros via interface
   - Filtros avançados
   - Paginação client-side

4. **Performance**
   - Cache de imagens
   - Lazy loading
   - Otimização de imagens no upload
   - Service Worker para PWA

5. **Produção**
   - Configurar CDN para imagens
   - Minificação de CSS/JS
   - Compressão de assets
   - Rate limiting para uploads

## Troubleshooting

### Imagens não aparecem
```bash
# Verifique se o diretório existe
ls -la media/books/covers/

# Verifique permissões
chmod -R 755 media/

# Verifique settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_URL)
>>> print(settings.MEDIA_ROOT)
```

### Erro de CORS
```python
# Adicione a origem em settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    # adicione outras origens aqui
]
```

### Token expirado
```javascript
// O sistema renova automaticamente
// Se persistir, limpe o localStorage
localStorage.clear()
```

## Documentação Adicional

- [FRONTEND_README.md](./FRONTEND_README.md) - Documentação detalhada do frontend
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Documentação da API
- [README.md](./README.md) - Documentação geral do projeto
