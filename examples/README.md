# Example Import Files

Este diretório contém arquivos de exemplo para importação em massa de dados para o sistema de gestão bibliotecária.

## Formatos Suportados

### 1. Arquivos TXT (Delimitado por pipe |)

#### Books (Livros)
**Formato**: `title|author|isbn|publisher|publication_year|category|quantity`

**Campos obrigatórios**:
- `title`: Título do livro
- `author`: Autor do livro
- `isbn`: ISBN (10 ou 13 dígitos)
- `quantity`: Quantidade total de cópias

**Campos opcionais**:
- `publisher`: Editora
- `publication_year`: Ano de publicação (numérico)
- `category`: Categoria/gênero

**Arquivo de exemplo**: [books_example.txt](books_example.txt)

#### Users (Usuários)
**Formato**: `full_name|email|phone|address|registration_number|is_active`

**Campos obrigatórios**:
- `full_name`: Nome completo
- `email`: Email único
- `registration_number`: Número de registro único

**Campos opcionais**:
- `phone`: Telefone
- `address`: Endereço
- `is_active`: Status (True/False, padrão: True)

**Arquivo de exemplo**: [users_example.txt](users_example.txt)

---

### 2. Arquivos Excel (.xlsx, .xls)

#### Books (Livros)
**Colunas**: `title`, `author`, `isbn`, `publisher`, `publication_year`, `category`, `quantity`

**Arquivo de exemplo**: [books_example.xlsx](books_example.xlsx)

#### Users (Usuários)
**Colunas**: `full_name`, `email`, `phone`, `address`, `registration_number`, `is_active`

**Arquivo de exemplo**: [users_example.xlsx](users_example.xlsx)

---

## Como Usar

### Via API (cURL)

#### Upload de Livros (TXT)
```bash
curl -X POST http://localhost:8000/api/books/bulk_upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/books_example.txt" \
  -F "file_type=txt"
```

#### Upload de Livros (Excel)
```bash
curl -X POST http://localhost:8000/api/books/bulk_upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/books_example.xlsx" \
  -F "file_type=excel"
```

#### Upload de Usuários (TXT)
```bash
curl -X POST http://localhost:8000/api/users/bulk_upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/users_example.txt" \
  -F "file_type=txt"
```

#### Upload de Usuários (Excel)
```bash
curl -X POST http://localhost:8000/api/users/bulk_upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/users_example.xlsx" \
  -F "file_type=excel"
```

### Via Interface Swagger

1. Acesse `http://localhost:8000/api/docs/`
2. Navegue até o endpoint de upload desejado
3. Clique em "Try it out"
4. Selecione o arquivo e o tipo (txt ou excel)
5. Clique em "Execute"

---

## Validações

### Livros
- ISBN deve ter 10 ou 13 dígitos
- ISBN deve ser único no sistema
- `quantity` deve ser um número positivo
- `publication_year` deve ser um número (se fornecido)

### Usuários
- Email deve ser único no sistema
- `registration_number` deve ser único no sistema
- Email deve estar em formato válido

---

## Tratamento de Erros

A API retorna um objeto JSON com:
```json
{
  "message": "Mensagem de sucesso ou erro",
  "created": 5,  // Número de registros criados
  "errors": []   // Lista de erros encontrados durante o processamento
}
```

Erros comuns:
- **Duplicação**: Registros com ISBN ou registration_number já existentes serão ignorados
- **Formato inválido**: Linhas com formato incorreto serão reportadas com número da linha
- **Dados faltando**: Campos obrigatórios ausentes causarão erro na linha específica

---

## Limitações

- Tamanho máximo de arquivo: 10MB
- Extensões aceitas:
  - TXT: `.txt`
  - Excel: `.xlsx`, `.xls`
- Encoding TXT: UTF-8

---

## Exemplo de Resposta de Sucesso

```json
{
  "message": "Successfully imported 5 books",
  "created": 5,
  "errors": []
}
```

## Exemplo de Resposta com Erros Parciais

```json
{
  "message": "Successfully imported 3 books",
  "created": 3,
  "errors": [
    "Line 3: Book with ISBN 9780743273565 already exists",
    "Line 5: Expected 7 fields, got 6"
  ]
}
```
