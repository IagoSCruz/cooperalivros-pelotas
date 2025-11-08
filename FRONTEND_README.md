# Frontend - Sistema de Gestão Bibliotecária

## Visão Geral

Interface web simples e moderna para o Sistema de Gestão Bibliotecária, construída com HTML, CSS e JavaScript puro (sem frameworks).

## Funcionalidades

### 1. Catálogo de Livros (`/`)
- **Visualização em grid** dos livros disponíveis
- **Busca em tempo real** por título, autor ou ISBN
- **Filtros**: Todos os livros ou apenas disponíveis
- **Modal de detalhes** ao clicar em um livro
- **Exibição de capas** dos livros (quando disponível)

### 2. Adicionar Livros (`/add-book`)
- **Formulário completo** para cadastro de livros:
  - Título, Autor, ISBN (obrigatórios)
  - Editora, Ano de Publicação, Categoria
  - Quantidade de exemplares
  - **Upload de imagem de capa**
- **Preview da imagem** antes do envio
- **Importação em massa** via arquivo:
  - Formato TXT (delimitado por `|`)
  - Formato Excel (.xlsx ou .xls)

### 3. Login (`/login`)
- Autenticação JWT
- Tokens armazenados no localStorage
- Refresh automático de tokens expirados

## Estrutura de Arquivos

```
livros-pel/
├── templates/              # Templates HTML
│   ├── base.html          # Template base com navbar e footer
│   ├── index.html         # Página de catálogo
│   ├── add_book.html      # Página de adicionar livro
│   └── login.html         # Página de login
│
├── web/static/            # Arquivos estáticos
│   ├── css/
│   │   └── style.css      # Estilos da aplicação
│   └── js/
│       ├── auth.js        # Utilitários de autenticação
│       ├── catalog.js     # Lógica do catálogo
│       ├── add-book.js    # Lógica de adicionar livro
│       └── login.js       # Lógica de login
│
├── frontend/              # App Django
│   ├── views.py           # Views que servem os templates
│   └── urls.py            # URLs do frontend
│
└── media/                 # Arquivos de upload
    └── books/covers/      # Imagens das capas
```

## API Endpoints Utilizados

### Livros
- `GET /api/books/` - Listar todos os livros
- `GET /api/books/available/` - Listar livros disponíveis
- `GET /api/books/{id}/` - Detalhes de um livro
- `POST /api/books/` - Criar novo livro
- `POST /api/books/{id}/upload_cover/` - Upload de capa
- `POST /api/books/bulk_upload/` - Importação em massa

### Autenticação
- `POST /api/auth/token/` - Login (obter tokens)
- `POST /api/auth/token/refresh/` - Renovar access token

## Como Usar

### 1. Iniciar o Servidor

```bash
poetry run python manage.py runserver
```

### 2. Acessar a Interface

Abra o navegador em: `http://localhost:8000`

### 3. Criar um Usuário (via Django Admin ou API)

```bash
poetry run python manage.py createsuperuser
```

### 4. Fazer Login

Acesse `/login` e utilize as credenciais criadas.

### 5. Adicionar Livros

#### Manualmente:
1. Vá para `/add-book`
2. Preencha o formulário
3. Opcionalmente, adicione uma imagem de capa
4. Clique em "Salvar Livro"

#### Importação em Massa:
1. Vá para `/add-book`
2. Role até a seção "Importação em Massa"
3. Selecione o tipo de arquivo (TXT ou Excel)
4. Faça upload do arquivo
5. Clique em "Importar Livros"

**Formato TXT:**
```
title|author|isbn|publisher|publication_year|category|quantity
O Senhor dos Anéis|J.R.R. Tolkien|9780544003415|HarperCollins|1954|Fantasia|5
Harry Potter|J.K. Rowling|9780439708180|Scholastic|1997|Fantasia|3
```

**Formato Excel:**
Planilha com colunas: `title`, `author`, `isbn`, `publisher`, `publication_year`, `category`, `quantity`

## Upload de Imagens

### Formatos Suportados
- JPG/JPEG
- PNG
- GIF
- WEBP

### Limitações
- Tamanho máximo: 10MB (configurável em settings.py)
- A imagem pode ser adicionada durante a criação ou posteriormente via endpoint

### Via API (para atualização posterior)

```bash
curl -X POST http://localhost:8000/api/books/{id}/upload_cover/ \
  -H "Authorization: Bearer {token}" \
  -F "cover_image=@/path/to/image.jpg"
```

## Autenticação

O frontend utiliza JWT (JSON Web Tokens) para autenticação:

### Fluxo de Autenticação
1. Usuário faz login
2. Backend retorna `access_token` e `refresh_token`
3. Tokens são armazenados no `localStorage`
4. Cada requisição inclui o header: `Authorization: Bearer {access_token}`
5. Se o token expirar, o sistema tenta renovar automaticamente
6. Se a renovação falhar, redireciona para login

### Segurança
- Tokens são armazenados apenas no navegador do usuário
- CORS configurado para aceitar apenas origens permitidas
- CSRF protection habilitado

## Configurações CORS

Em `config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

## Customização

### Alterar Cores
Edite as variáveis CSS em `web/static/css/style.css`:

```css
:root {
    --primary-color: #2563eb;      /* Azul primário */
    --primary-dark: #1d4ed8;       /* Azul escuro */
    --secondary-color: #64748b;    /* Cinza */
    --success-color: #10b981;      /* Verde */
    --danger-color: #ef4444;       /* Vermelho */
    /* ... */
}
```

### Adicionar Novas Páginas
1. Crie o template em `templates/`
2. Adicione a view em `frontend/views.py`
3. Registre a URL em `frontend/urls.py`

### Modificar Comportamento da API
Edite os arquivos JavaScript correspondentes em `web/static/js/`

## Responsividade

O frontend é totalmente responsivo e funciona bem em:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Melhorias Futuras

- [ ] Página de gerenciamento de empréstimos
- [ ] Página de perfil do usuário
- [ ] Modo escuro
- [ ] Paginação no frontend
- [ ] Filtros avançados (por categoria, ano, etc.)
- [ ] Edição de livros via interface
- [ ] Exclusão de livros via interface
- [ ] Notificações toast para ações
- [ ] Loading spinners mais elaborados
- [ ] Cache de imagens
- [ ] PWA (Progressive Web App)

## Troubleshooting

### Imagens não aparecem
- Verifique se `MEDIA_URL` e `MEDIA_ROOT` estão configurados corretamente
- Certifique-se de que o diretório `media/` existe e tem permissões de escrita
- Em produção, configure o servidor web (nginx/apache) para servir arquivos de mídia

### Erro de CORS
- Adicione a origem do frontend em `CORS_ALLOWED_ORIGINS` no settings.py
- Certifique-se de que `corsheaders` está instalado e configurado

### Token expirado
- O sistema tenta renovar automaticamente
- Se persistir, faça logout e login novamente
- Verifique as configurações de `ACCESS_TOKEN_LIFETIME` em settings.py

### Upload de arquivo falha
- Verifique o tamanho do arquivo (máx 10MB)
- Confirme que o formato é suportado
- Verifique se o usuário está autenticado
