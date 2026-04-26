# Guia de Onboarding Técnico: Projeto Griô

Bem-vindo ao onboarding técnico do **Griô**! Este documento foi elaborado para guiar você (e futuros desenvolvedores ou IAs) pela arquitetura, stack tecnológica e particularidades do ambiente de desenvolvimento. O objetivo é que você possa retomar o código a qualquer momento sabendo exatamente onde as coisas estão e o porquê de cada decisão técnica.

---

## 1. Visão Geral da Arquitetura

O projeto é um **Monorepo** dividido claramente em duas grandes áreas:
*   **Backend**: API em Python com FastAPI, responsável por toda a lógica de negócios, autenticação e comunicação com os bancos de dados.
*   **Frontend**: Aplicação SPA/SSR moderna feita com SvelteKit.

Trabalhamos com uma arquitetura **Poliglota de Persistência** (dois bancos de dados rodando simultaneamente):
1.  **PostgreSQL**: Armazena dados relacionais clássicos (Usuários e, no futuro, as Questões em si).
2.  **Neo4j**: Banco de dados em Grafos. Ele armazena os **Conceitos** (ex: Matemática Básica, Interpretação de Texto) e a relação de **Proficiência** que o usuário tem com eles `(User)-[HAS_PROFICIENCY]->(Concept)`.

---

## 2. Estrutura de Diretórios (Backend)

O backend segue um padrão arquitetural limpo para FastAPI:

```text
backend/
├── api/v1/endpoints/  # Controladores da API. Recebem as requisições e enviam para o CRUD.
├── core/              # Configurações sensíveis e injeções de dependências (ex: deps.py, security.py, neo4j.py).
├── crud/              # Lógica de banco de dados (Create, Read, Update, Delete). É aqui que rodam as querys SQLAlchemy e Cypher (Neo4j).
├── models/            # Modelos do SQLAlchemy (Representação das tabelas no PostgreSQL).
├── schemas/           # Modelos do Pydantic (Validação de entrada/saída das APIs. Tipagem estrita).
├── tests/             # Suíte de testes automatizados usando pytest.
├── main.py            # Ponto de entrada da aplicação FastAPI. Registra os "routers" e o middleware de CORS.
├── database.py        # Configuração da conexão com o banco de dados PostgreSQL.
├── Dockerfile         # Receita para criar o container do backend.
└── requirements.txt   # Dependências do Python.
```

---

## 3. Entendendo o Ambiente Docker

Para facilitar o desenvolvimento, tudo o que o backend precisa roda em containers orquestrados pelo `docker-compose.yml` na raiz do projeto.

Ao rodar `docker-compose up -d --build`, ele levanta os seguintes serviços:
1.  **postgres**: Banco relacional na porta `5432`.
2.  **neo4j**: Banco de grafos na porta `7687` (bolt) e interface de visualização em `http://localhost:7474`.
3.  **backend**: Nossa API rodando na porta `8000` (`http://localhost:8000`).

**Como interagir com o backend Dockerizado:**
*   **Reiniciar a API:** Se você alterar código fora das pastas dinâmicas ou precisar forçar um reinício:
    `docker-compose restart backend`
*   **Ver Logs da API:** 
    `docker-compose logs -f backend`

---

## 4. O Sistema de Testes (Pytest)

Configuramos uma suíte de testes muito robusta na pasta `backend/tests/`.
Para testar, você não precisa se preocupar com dados sendo sujos no banco principal. Nós configuramos o arquivo `conftest.py` para levantar um **banco SQLite em memória** que roda exclusivo para os testes.

**Comando para rodar testes:**
```bash
docker-compose exec backend pytest -v
```

> **Atenção (Gotcha Técnico):** Nós usamos a classe `StaticPool` no SQLite dos testes (`conftest.py`). Isso foi necessário porque a API cria o banco na inicialização do teste, e se não fosse o `StaticPool`, as rotas do FastAPI não encontrariam as tabelas devido ao SQLite em memória isolar os dados por *thread/conexão*. Com o `StaticPool`, garantimos que o teste rode fluido e sem o erro `no such table`.

---

## 5. Autenticação e Segurança

Implementamos o fluxo completo de autenticação via **HttpOnly Cookies**:

*   **Hashing de Senhas**: Usamos a biblioteca oficial **`bcrypt`**.
*   **Segurança JWT**: O token não é mais armazenado no `localStorage`, prevenindo ataques XSS. Ele é trafegado via Cookie HttpOnly.
*   **Dependência `get_current_user`**: Se você for criar uma nova rota que precisa de login (ex: `/perfil`), basta passar isso no endpoint:
    ```python
    def meu_endpoint(user: User = Depends(get_current_user)):
    ```

---

## 6. Frontend (SvelteKit)

Localizado na pasta `frontend/`. O SvelteKit é focado em simplicidade reativa.

*   **Design System (`src/app.css`)**: Não estamos usando frameworks como Tailwind ou Bootstrap. Desenvolvemos nossa própria folha de estilo usando **Variáveis CSS** no topo do arquivo. Nosso tema atual é o "Liquid Glass 2.0", focado em fundos escuros (#0A0A0B), bordas finas e detalhes neon por Área do Conhecimento.
*   **Fluxo de Páginas**: 
    - As páginas ficam em `src/routes/`.
    - Os formulários e componentes ficam em `src/lib/components/`.
*   **Autenticação**: O frontend envia `credentials: 'include'` em todas as requisições para que o navegador anexe automaticamente o Cookie JWT.

---

## 7. Como Iniciar o Desenvolvimento Diário (Workflow)

Seu dia a dia no projeto deve seguir estes passos básicos:

1. **Garantir que a base de dados e a API estão rodando:**
   ```bash
   docker-compose up -d
   ```
2. **Rodar o servidor de desenvolvimento do Frontend:**
   Abra um novo terminal.
   ```bash
   cd frontend
   npm run dev
   ```
   Acesse a aplicação no seu navegador: `http://localhost:5173`.
3. **Checar a documentação viva da API:**
   A qualquer momento, você pode ver todos os endpoints que o backend possui (e testá-los diretamente pelo navegador) acessando: `http://localhost:8000/docs`.

---

## 8. Dívidas Técnicas Resolvidas & Próximos Passos (To-Do)

1. **Auth Segura**: Migrado para HttpOnly Cookies (✅ Resolvido).
2. **Módulo de Prática (Estudar Conceito)**: Lógica de Micro-aulas e Mentor Socrático implementadas e persistidas no Grafo (✅ Resolvido).
3. **Experiência Area-First (Griô 2.0)**: Pivot estratégico finalizado. Dashboard baseado em grandes Áreas, layout Liquid Glass 2.0 e navegação focada em ecossistema (✅ Resolvido).
4. **Banco de Questões Reais**: Povoar o banco PostgreSQL com dados reais de vestibulares, associando cada questão a uma `Concept` do Neo4j (Em andamento).

Boa sorte! A fundação do Griô está sólida como rocha e pronta para escalar.
