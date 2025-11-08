# ATIVIDADE EXTENSIONISTA
## Sistema de Gestão Bibliotecária (Livros PEL)

---

## 1. IDENTIFICAÇÃO DO PROJETO

**Título do Projeto:** Sistema de Gestão Bibliotecária para Promoção da Inclusão Digital (Livros PEL)

**Área de Conhecimento:** Ciência da Computação / Engenharia de Software

**Linha de Extensão:** Tecnologia e Produção / Inclusão Digital

**Público-Alvo:** Bibliotecas comunitárias, instituições educacionais e comunidades com recursos tecnológicos limitados

**Período de Execução:** Novembro 2024 - Presente

**Coordenador/Desenvolvedor:** Iago Cruz (iagosilvacontato@gmail.com)

---

## 2. CARACTERIZAÇÃO DA ATIVIDADE EXTENSIONISTA

### 2.1 Contextualização do Problema Social

Em comunidades com recursos tecnológicos limitados, a gestão de acervos bibliográficos frequentemente ocorre de forma manual ou por meio de planilhas dispersas, dificultando:

- **Controle eficiente** de empréstimos e devoluções
- **Acesso democrático** ao conhecimento disponível
- **Rastreabilidade** de livros e histórico de usuários
- **Escalabilidade** do serviço bibliotecário
- **Inclusão digital** de gestores e usuários

### 2.2 Justificativa Social

O projeto atende diretamente às demandas de:

1. **Democratização do Acesso à Informação:** Facilita o acesso gratuito e organizado a acervos bibliográficos
2. **Inclusão Digital:** Interface intuitiva permite que pessoas com baixa literacia digital utilizem tecnologia moderna
3. **Empoderamento Comunitário:** Comunidades ganham autonomia na gestão de seus recursos educacionais
4. **Sustentabilidade:** Redução de custos com software proprietário e infraestrutura
5. **Educação:** Promove a leitura e o acesso ao conhecimento em comunidades vulneráveis

### 2.3 Objetivos da Atividade Extensionista

#### Objetivo Geral
Desenvolver e disponibilizar um sistema web open-source de gestão bibliotecária que promova a inclusão digital e facilite o acesso democrático ao conhecimento em comunidades com recursos tecnológicos limitados.

#### Objetivos Específicos
1. Criar ferramenta tecnológica acessível para gestão de acervos bibliográficos
2. Implementar funcionalidades que automatizem processos manuais de empréstimo/devolução
3. Disponibilizar sistema gratuitamente para replicação em outras comunidades
4. Promover inclusão digital através de interface intuitiva e documentação completa
5. Estabelecer ponte entre conhecimento acadêmico (engenharia de software) e necessidades sociais reais
6. Documentar todo o processo para transferência de tecnologia

---

## 3. FUNDAMENTAÇÃO TEÓRICA E TECNOLÓGICA

### 3.1 Inclusão Digital e Acesso à Informação

A inclusão digital vai além do acesso à tecnologia - envolve a capacidade de utilizar recursos tecnológicos para melhorar qualidade de vida e acesso a direitos. O projeto aplica princípios de:

- **Usabilidade:** Interface simplificada para públicos diversos
- **Acessibilidade:** Compatibilidade com diversos dispositivos e navegadores
- **Documentação:** Guias completos para instalação e uso
- **Open Source:** Código aberto permite adaptação às necessidades locais

### 3.2 Arquitetura de Software para Contextos de Recursos Limitados

O projeto implementa **Arquitetura Evolutiva**, permitindo:

- Início com persistência em arquivos TXT (baixo custo)
- Migração gradual para banco de dados conforme necessidade
- Escalabilidade horizontal quando recursos aumentam
- Flexibilidade para diferentes contextos de implantação

### 3.3 Padrões de Engenharia de Software Aplicados

**Repository Pattern:** Abstração da camada de dados facilita migração tecnológica
**API RESTful:** Permite integração futura com outros sistemas
**MVC/MVT:** Separação de responsabilidades facilita manutenção
**Documentação Automática:** Reduz curva de aprendizado para novos desenvolvedores

---

## 4. METODOLOGIA DE DESENVOLVIMENTO

### 4.1 Abordagem Técnica

**Framework Escolhido:** Django 5.2.7 (Python)
- **Justificativa:** Maturidade, documentação extensa, comunidade ativa, curva de aprendizado moderada

**Arquitetura:** Monolítica com separação em Apps (Books, Users, Loans)
- **Justificativa:** Simplicidade de deploy e manutenção para contextos com recursos limitados

**Banco de Dados:** SQLite (dev) / PostgreSQL (produção)
- **Justificativa:** SQLite não requer servidor (zero config), PostgreSQL oferece escalabilidade

### 4.2 Processo de Desenvolvimento

1. **Levantamento de Requisitos:** Pesquisa sobre necessidades de bibliotecas comunitárias
2. **Modelagem de Dados:** Entidades Book, LibraryUser, Loan com relacionamentos adequados
3. **Implementação Iterativa:** Desenvolvimento incremental com testes automatizados
4. **Documentação Contínua:** README, API docs, guias de instalação
5. **Testes de Usabilidade:** Validação com perfis diversos de usuários
6. **Deploy e Distribuição:** Containerização Docker para facilitar instalação

### 4.3 Boas Práticas Implementadas

- **Testes Automatizados:** Pytest com cobertura > 80%
- **Linting/Formatting:** Ruff para qualidade de código
- **CI/CD:** GitHub Actions para integração contínua
- **Versionamento:** Git com commits semânticos
- **Documentação:** Inline docs, README extensivo, API interativa
- **Segurança:** JWT authentication, CSRF protection, validações robustas

---

## 5. RESULTADOS E IMPACTOS

### 5.1 Produto Desenvolvido

**Sistema Web Completo com:**
- ✅ Cadastro e gerenciamento de livros (CRUD)
- ✅ Cadastro e gerenciamento de usuários (CRUD)
- ✅ Sistema de empréstimos com controle automático de prazos
- ✅ Upload em massa via arquivos TXT/Excel
- ✅ API REST documentada (Swagger/ReDoc)
- ✅ Autenticação JWT para segurança
- ✅ Interface web intuitiva
- ✅ Controle automático de disponibilidade de livros
- ✅ Identificação de empréstimos atrasados
- ✅ Relatórios de status (ativos, atrasados, disponíveis)

### 5.2 Artefatos Gerados

1. **Código-Fonte:** Disponível publicamente com licença open-source
2. **Documentação Técnica:**
   - README.md completo
   - API_DOCUMENTATION.md (endpoints, exemplos, validações)
   - AUTHENTICATION_GUIDE.md (segurança e JWT)
   - FRONTEND_README.md (interface do usuário)
   - QUICKSTART.md (instalação rápida)
3. **Diagramas:**
   - architecture_diagram.html (diagrama interativo)
   - Memorando técnico com análise arquitetural
4. **Testes:** Suite completa com 80%+ cobertura
5. **Exemplos:** Arquivos TXT/Excel para importação rápida
6. **Docker:** Containerização para deploy facilitado

### 5.3 Impacto Social Esperado

#### Direto
- **Bibliotecas Comunitárias:** Gestão eficiente de acervos sem custo de software
- **Usuários Finais:** Acesso facilitado a livros disponíveis
- **Gestores:** Redução de trabalho manual e erros humanos
- **Estudantes:** Melhor experiência de empréstimo e devolução

#### Indireto
- **Inclusão Digital:** Familiarização com sistemas web modernos
- **Fomento à Leitura:** Facilidade de acesso incentiva empréstimos
- **Transferência de Tecnologia:** Código aberto permite replicação
- **Formação Técnica:** Documentação permite aprendizado de desenvolvedores iniciantes

### 5.4 Métricas de Sucesso

**Técnicas:**
- ✅ Sistema funcional com todas as funcionalidades planejadas
- ✅ Testes automatizados com cobertura > 80%
- ✅ Documentação completa e acessível
- ✅ API RESTful documentada automaticamente
- ✅ Deploy via Docker (portabilidade)

**Extensionistas:**
- 🎯 Código open-source disponível publicamente
- 🎯 Documentação permite replicação por terceiros
- 🎯 Arquitetura evolutiva atende contextos diversos
- 🎯 Interface acessível para públicos com baixa literacia digital

---

## 6. DIAGRAMAS E ARQUITETURA

### 6.1 Diagrama de Arquitetura

O sistema foi desenvolvido seguindo arquitetura em camadas com separação clara de responsabilidades:

```
[APRESENTAÇÃO]
   ↓
[APLICAÇÃO - Django Apps]
   ↓
[SEGURANÇA - JWT/CORS]
   ↓
[PROCESSAMENTO - File Processors]
   ↓
[PERSISTÊNCIA - ORM/Database]
```

**Arquivo de referência:** `architecture_diagram.html`
- Diagrama interativo HTML com todas as camadas
- Componentes detalhados por app
- Fluxos de dados documentados
- Relacionamentos de banco de dados
- Stack tecnológica completa

### 6.2 Modelo de Dados

**Entidades Principais:**

1. **Book (Livro)**
   - Atributos: title, author, isbn (unique), publisher, publication_year, category
   - Controle: quantity, available_quantity, cover_image
   - Métodos: is_available(), reserve_copy(), return_copy()

2. **LibraryUser (Usuário da Biblioteca)**
   - Atributos: full_name, email (unique), phone, address
   - Identificador: registration_number (unique)
   - Status: is_active (controle de permissão para empréstimos)

3. **Loan (Empréstimo)**
   - Relacionamentos: book (FK), user (FK)
   - Datas: loan_date, due_date, return_date
   - Status: ACTIVE, RETURNED, OVERDUE, RENEWED
   - Métodos: is_overdue(), mark_as_returned(), days_overdue()

**Relacionamentos:**
- Loan.book → Book (ForeignKey, PROTECT)
- Loan.user → LibraryUser (ForeignKey, PROTECT)
- Proteção contra exclusão acidental de dados com empréstimos ativos

### 6.3 Fluxos Operacionais

**Fluxo de Empréstimo:**
1. Usuário solicita livro
2. Sistema valida: usuário ativo + livro disponível
3. Loan criado com status ACTIVE
4. Book.reserve_copy() reduz available_quantity
5. Due_date calculado (+14 dias)

**Fluxo de Devolução:**
1. Biblioteca marca empréstimo como devolvido
2. Loan.mark_as_returned() atualiza status
3. Book.return_copy() incrementa available_quantity
4. Sistema registra return_date

**Fluxo de Upload em Massa:**
1. Upload de arquivo TXT/Excel
2. FileProcessor processa linha a linha
3. Validações executadas
4. Criação em lote
5. Retorno com summary (sucessos + erros)

---

## 7. ARTICULAÇÃO TEORIA-PRÁTICA

### 7.1 Conhecimentos Acadêmicos Aplicados

**Engenharia de Software:**
- Padrões de projeto (Repository, MVC, Service Layer)
- Arquitetura de software (camadas, separação de responsabilidades)
- Testes automatizados (TDD, cobertura de código)
- Documentação técnica

**Banco de Dados:**
- Modelagem relacional (entidades, relacionamentos)
- Normalização de dados (3FN)
- Otimização de queries (índices)
- Integridade referencial

**Desenvolvimento Web:**
- API RESTful (recursos, métodos HTTP, status codes)
- Autenticação e autorização (JWT, permissions)
- Segurança web (CSRF, XSS, SQL injection prevention)
- CORS e integração frontend/backend

**DevOps:**
- Containerização (Docker, Docker Compose)
- CI/CD (GitHub Actions)
- Gerenciamento de configurações (environment variables)
- Deploy e versionamento

### 7.2 Aprendizados Adquiridos

1. **Desenvolvimento para Contextos Reais:** Necessidade de balancear funcionalidades avançadas com simplicidade de uso
2. **Arquitetura Evolutiva:** Importância de projetar sistemas que possam crescer gradualmente
3. **Documentação é Extensão:** Código bem documentado facilita transferência de tecnologia
4. **Testes Automatizados:** Garantem qualidade e facilitam manutenção futura
5. **Open Source:** Compartilhamento de conhecimento multiplica impacto social

---

## 8. CONSIDERAÇÕES FINAIS

### 8.1 Desafios Enfrentados

1. **Balanceamento:** Recursos avançados vs. simplicidade de uso
2. **Escalabilidade:** Arquitetar sistema que funcione tanto para 100 quanto para 10.000 livros
3. **Documentação:** Criar documentação técnica acessível para não-programadores
4. **Testes:** Garantir cobertura adequada sem comprometer velocidade de desenvolvimento

### 8.2 Lições Aprendidas

- **Simplicidade é fundamental:** Interface intuitiva é mais importante que muitas features
- **Documentação é produto:** Tão importante quanto o código
- **Testes economizam tempo:** Bugs encontrados cedo custam menos
- **Comunidade importa:** Código open-source tem potencial de impacto multiplicado

### 8.3 Contribuição para Formação Profissional

O projeto consolidou conhecimentos técnicos (Django, REST APIs, DevOps) e desenvolveu competências sociais:
- **Empatia:** Entender necessidades de públicos diversos
- **Comunicação:** Documentar para audiências técnicas e não-técnicas
- **Responsabilidade Social:** Tecnologia como ferramenta de transformação social
- **Visão Sistêmica:** Compreender impactos além do código

### 8.4 Perspectivas Futuras

**Curto Prazo:**
- Deploy piloto em biblioteca comunitária
- Coleta de feedback de usuários reais
- Ajustes de usabilidade baseados em testes

**Médio Prazo:**
- Sistema de notificações (email/SMS)
- Relatórios e dashboards
- Frontend responsivo moderno
- Sistema de multas

**Longo Prazo:**
- Integração com catálogos externos (ISBN APIs)
- Sistema de reservas (fila de espera)
- Aplicativo mobile
- Comunidade de desenvolvedores contribuindo

---

## 9. REFERÊNCIAS

### Tecnológicas
- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Python Official Documentation: https://docs.python.org/

### Padrões e Boas Práticas
- Martin, R. C. (2017). Clean Architecture: A Craftsman's Guide to Software Structure and Design
- Fowler, M. (2002). Patterns of Enterprise Application Architecture
- Richardson, C. (2018). Microservices Patterns

### Inclusão Digital
- Silveira, S. A. (2001). Exclusão Digital: A Miséria na Era da Informação
- Warschauer, M. (2006). Tecnologia e Inclusão Social: A Exclusão Digital em Debate

---

## 10. ANEXOS

### Anexo A - Links Importantes
- **Repositório:** [URL do GitHub - se público]
- **Documentação Online:** [URL da documentação - se hospedada]
- **Diagrama Interativo:** architecture_diagram.html

### Anexo B - Evidências
- Screenshots da interface web
- Capturas da API documentada (Swagger)
- Logs de testes automatizados
- Métricas de cobertura de código

### Anexo C - Documentação Técnica Completa
- README.md
- API_DOCUMENTATION.md
- AUTHENTICATION_GUIDE.md
- FRONTEND_README.md
- QUICKSTART.md
- UPDATES.md

---

## DECLARAÇÃO

Declaro que o presente projeto de atividade extensionista foi desenvolvido com o objetivo de aplicar conhecimentos acadêmicos na resolução de problemas sociais reais, promovendo a inclusão digital e o acesso democrático ao conhecimento por meio da tecnologia.

O código-fonte está disponível como software livre, permitindo replicação e adaptação por outras instituições e comunidades, maximizando o impacto social da iniciativa.

---

**Desenvolvedor:** Iago Cruz
**Email:** iagosilvacontato@gmail.com
**Data:** Novembro de 2025
**Instituição:** [Nome da Instituição de Ensino]
**Curso:** [Nome do Curso]
