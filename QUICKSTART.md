# Guia de Início Rápido - Sistema de Gestão Bibliotecária

## Setup Inicial (5 minutos)

### 1. Instalação
```bash
# Clone o repositório (se ainda não fez)
git clone <repository-url>
cd livros-pel

# Instale as dependências
poetry install
```

### 2. Configuração do Banco de Dados
```bash
# Execute as migrações
poetry run python manage.py migrate

# Crie um superusuário
poetry run python manage.py createsuperuser
# Digite: username, email, password
```

### 3. Inicie o Servidor
```bash
poetry run python manage.py runserver
```

## Acessando a Aplicação

### Frontend (Interface Web)
- **Catálogo**: http://localhost:8000/
- **Adicionar Livro**: http://localhost:8000/add-book
- **Login**: http://localhost:8000/login

### API (Backend)
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/

## Fluxo de Uso Típico

### 1. Fazer Login
1. Acesse: http://localhost:8000/login
2. Digite suas credenciais de superusuário
3. Clique em "Entrar"

### 2. Adicionar Livros

#### Método 1: Individual
1. Acesse: http://localhost:8000/add-book
2. Preencha o formulário:
   - **Título**: Ex: "Clean Code"
   - **Autor**: Ex: "Robert C. Martin"
   - **ISBN**: Ex: "9780132350884" (10 ou 13 dígitos)
   - **Editora** (opcional): Ex: "Prentice Hall"
   - **Ano** (opcional): Ex: 2008
   - **Categoria** (opcional): Ex: "Programação"
   - **Quantidade**: Ex: 3
3. Opcionalmente, adicione uma imagem de capa
4. Clique em "Salvar Livro"

#### Método 2: Importação em Massa (TXT)
1. Crie um arquivo `livros.txt`:
```
title|author|isbn|publisher|publication_year|category|quantity
Clean Code|Robert C. Martin|9780132350884|Prentice Hall|2008|Programação|3
The Pragmatic Programmer|Andrew Hunt|9780135957059|Addison-Wesley|2019|Programação|2
Domain-Driven Design|Eric Evans|9780321125217|Addison-Wesley|2003|Arquitetura|1
```

2. Acesse: http://localhost:8000/add-book
3. Role até "Importação em Massa"
4. Selecione "TXT"
5. Faça upload do arquivo
6. Clique em "Importar Livros"

#### Método 3: Importação em Massa (Excel)
1. Crie uma planilha Excel com colunas:
   - title
   - author
   - isbn
   - publisher
   - publication_year
   - category
   - quantity

2. Preencha com seus dados
3. Acesse: http://localhost:8000/add-book
4. Role até "Importação em Massa"
5. Selecione "Excel"
6. Faça upload do arquivo
7. Clique em "Importar Livros"

### 3. Visualizar Catálogo
1. Acesse: http://localhost:8000/
2. Veja todos os livros em formato de grid
3. Use a busca para encontrar livros específicos
4. Filtre por "Disponíveis" se necessário
5. Clique em um livro para ver detalhes completos

### 4. Adicionar Imagem a um Livro Existente

#### Via Frontend:
1. Crie um novo livro com a imagem já incluída no formulário

#### Via API:
```bash
# 1. Faça login para obter o token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'

# Copie o "access" token da resposta

# 2. Faça upload da imagem
curl -X POST http://localhost:8000/api/books/1/upload_cover/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "cover_image=@/caminho/para/imagem.jpg"
```

## Exemplos de Dados para Teste

### Livros de Programação
```
Clean Code|Robert C. Martin|9780132350884|Prentice Hall|2008|Programação|3
Design Patterns|Erich Gamma|9780201633610|Addison-Wesley|1994|Programação|2
Refactoring|Martin Fowler|9780201485677|Addison-Wesley|1999|Programação|2
The Pragmatic Programmer|Andrew Hunt|9780135957059|Addison-Wesley|2019|Programação|4
Code Complete|Steve McConnell|9780735619678|Microsoft Press|2004|Programação|2
```

### Clássicos da Literatura
```
1984|George Orwell|9780451524935|Signet Classic|1949|Ficção|5
O Grande Gatsby|F. Scott Fitzgerald|9780743273565|Scribner|1925|Ficção|3
Dom Casmurro|Machado de Assis|9788535908799|Penguin|1899|Romance|4
Cem Anos de Solidão|Gabriel García Márquez|9780060883287|Harper|1967|Ficção|2
O Senhor dos Anéis|J.R.R. Tolkien|9780544003415|HarperCollins|1954|Fantasia|6
```

## Comandos Úteis

### Desenvolvimento
```bash
# Executar servidor
poetry run task run

# Executar testes
poetry run task test

# Verificar código
poetry run task lint

# Formatar código
poetry run task format

# Criar migrações
poetry run task makemigrations

# Aplicar migrações
poetry run task migrate

# Abrir shell Django
poetry run task shell
```

### Dados
```bash
# Backup do banco de dados
cp db.sqlite3 db.backup.sqlite3

# Resetar banco de dados (CUIDADO!)
rm db.sqlite3
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### Docker
```bash
# Iniciar com Docker
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f
```

## Troubleshooting Comum

### "No such table: books_book"
```bash
poetry run python manage.py migrate
```

### "Port 8000 is already in use"
```bash
# Mude a porta
poetry run python manage.py runserver 8001

# Ou mate o processo
lsof -ti:8000 | xargs kill -9
```

### "ModuleNotFoundError: No module named 'PIL'"
```bash
poetry add pillow
```

### Imagens não aparecem
```bash
# Crie o diretório
mkdir -p media/books/covers

# Verifique permissões
chmod -R 755 media/
```

### Erro de CORS
Adicione em `config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

## Próximos Passos

1. ✅ Sistema funcionando localmente
2. ✅ Frontend acessível
3. ✅ Livros cadastrados
4. 📚 Explore a documentação da API: http://localhost:8000/api/docs/
5. 🔧 Personalize o sistema conforme suas necessidades
6. 📊 Implemente relatórios e estatísticas
7. 🚀 Faça deploy em produção

## Recursos Adicionais

- [README.md](./README.md) - Documentação completa do projeto
- [FRONTEND_README.md](./FRONTEND_README.md) - Documentação do frontend
- [UPDATES.md](./UPDATES.md) - Atualizações recentes
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Documentação da API

## Precisa de Ajuda?

- Consulte a documentação: http://localhost:8000/api/docs/
- Verifique os logs do servidor no terminal
- Revise os arquivos de configuração em `config/settings.py`
- Entre em contato: iagosilvacontato@gmail.com
