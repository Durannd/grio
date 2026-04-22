# Plataforma de Estudos (MVP Matemática) - Plano de Implementação

> **Para agentes:** É OBRIGATÓRIO usar a sub-skill `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa por tarefa. Os passos usam a sintaxe de checkbox (`- [ ]`) para rastreamento.

**Objetivo:** Construir o backend e a estrutura inicial do frontend para o MVP de Matemática, focando no onboarding do usuário e na estrutura de dados.

**Arquitetura:** Backend em Python/FastAPI com PostgreSQL para dados relacionais e Neo4j para o grafo de conhecimento. Frontend em Svelte/SvelteKit.

**Stack Tecnológica:** Python, FastAPI, PostgreSQL, Neo4j, SvelteKit, Docker.

---

### Tarefa 1: Configuração do Projeto e Docker

**Arquivos:**
- Criar: `docker-compose.yml`
- Criar: `backend/Dockerfile`
- Criar: `backend/requirements.txt`
- Criar: `frontend/Dockerfile`

- [ ] **Passo 1: Criar o `docker-compose.yml` para orquestrar os serviços.**
  ```yaml
  version: '3.8'
  services:
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      volumes:
        - ./backend:/app
      environment:
        - DATABASE_URL=postgresql://user:password@db:5432/studydb
        - NEO4J_URI=bolt://neo4j:7687
        - NEO4J_USER=neo4j
        - NEO4J_PASSWORD=password
      depends_on:
        - db
        - neo4j
    db:
      image: postgres:13
      volumes:
        - postgres_data:/var/lib/postgresql/data/
      environment:
        - POSTGRES_USER=user
        - POSTGRES_PASSWORD=password
        - POSTGRES_DB=studydb
    neo4j:
      image: neo4j:4.4
      ports:
        - "7474:7474"
        - "7687:7687"
      volumes:
        - neo4j_data:/data
      environment:
        - NEO4J_AUTH=neo4j/password
    frontend:
      build: ./frontend
      ports:
        - "5173:5173"
      volumes:
        - ./frontend:/app
        - /app/node_modules

  volumes:
    postgres_data:
    neo4j_data:
  ```

- [ ] **Passo 2: Criar os arquivos do backend.**
  **`backend/requirements.txt`**
  ```txt
  fastapi
  uvicorn[standard]
  sqlalchemy
  psycopg2-binary
  neo4j
  pydantic
  ```
  **`backend/Dockerfile`**
  ```dockerfile
  FROM python:3.9
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  ```

- [ ] **Passo 3: Criar o arquivo principal inicial do backend (`backend/main.py`).**
  ```python
  from fastapi import FastAPI

  app = FastAPI()

  @app.get("/")
  def read_root():
      return {"message": "API da Plataforma de Estudos no ar!"}
  ```

- [ ] **Passo 4: Criar os arquivos do frontend.**
  *Primeiro, inicialize um projeto SvelteKit localmente se necessário, depois crie o Dockerfile.*
  **`frontend/Dockerfile`**
  ```dockerfile
  FROM node:18
  WORKDIR /app
  COPY package*.json ./
  RUN npm install
  COPY . .
  EXPOSE 5173
  CMD ["npm", "run", "dev", "--", "--host"]
  ```

- [ ] **Passo 5: Subir os contêineres e verificar se tudo funciona.**
  Executar: `docker-compose up --build -d`
  Verificar:
  - Acessar `http://localhost:8000` e ver a mensagem da API.
  - Acessar `http://localhost:5173` e ver a página inicial do SvelteKit.
  - Acessar `http://localhost:7474` e ver a interface do Neo4j.

- [ ] **Passo 6: Commit.**
  ```bash
  git add .
  git commit -m "feat: setup initial project structure with Docker"
  ```

### Tarefa 2: Modelo de Usuário e Autenticação (Backend)

**Arquivos:**
- Criar: `backend/models/user.py`
- Criar: `backend/schemas/user.py`
- Criar: `backend/crud/user.py`
- Criar: `backend/api/v1/endpoints/users.py`
- Modificar: `backend/main.py`
- Testar: `backend/tests/test_users.py`

- [ ] **Passo 1: Escrever o teste que falha para criação de usuário.**
  **`backend/tests/test_users.py`**
  ```python
  from fastapi.testclient import TestClient
  from backend.main import app

  client = TestClient(app)

  def test_create_user():
      response = client.post(
          "/api/v1/users/",
          json={"email": "test@example.com", "password": "password123"},
      )
      assert response.status_code == 200
      data = response.json()
      assert data["email"] == "test@example.com"
      assert "id" in data
  ```

- [ ] **Passo 2: Executar o teste e verificar a falha.**
  Executar: `pytest backend/tests/test_users.py`
  Esperado: FALHA (endpoint não existe).

- [ ] **Passo 3: Implementar o mínimo para o teste passar.**
  **`backend/models/user.py`** (Modelo SQLAlchemy)
  ```python
  from sqlalchemy import Column, Integer, String
  from backend.database import Base

  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True, index=True)
      email = Column(String, unique=True, index=True)
      hashed_password = Column(String)
  ```
  **`backend/schemas/user.py`** (Esquema Pydantic)
  ```python
  from pydantic import BaseModel

  class UserCreate(BaseModel):
      email: str
      password: str

  class User(BaseModel):
      id: int
      email: str
      class Config:
          orm_mode = True
  ```
  **`backend/api/v1/endpoints/users.py`**
  ```python
  from fastapi import APIRouter, Depends
  from sqlalchemy.orm import Session
  from backend.schemas.user import User, UserCreate
  from backend.crud import user as crud_user
  from backend.database import get_db

  router = APIRouter()

  @router.post("/", response_model=User)
  def create_user(user: UserCreate, db: Session = Depends(get_db)):
      db_user = crud_user.create_user(db=db, user=user)
      return db_user
  ```
  *Será necessário criar os arquivos `database.py` e `crud/user.py` de forma similar.*

- [ ] **Passo 4: Executar o teste e verificar o sucesso.**
  Executar: `pytest backend/tests/test_users.py`
  Esperado: SUCESSO.

- [ ] **Passo 5: Commit.**
  ```bash
  git add backend/
  git commit -m "feat: add user creation endpoint and model"
  ```
---

Este é o início do plano. Ele continuaria com tarefas para:
- **Tarefa 3:** Cadastro e Login no Frontend.
- **Tarefa 4:** Definição dos modelos do Grafo em Neo4j.
- **Tarefa 5:** Implementação da Prova de Nivelamento (backend).
- **Tarefa 6:** Implementação da Prova de Nivelamento (frontend).
- **Tarefa 7:** Geração da Trilha de Aprendizado inicial.
- etc.

Cada tarefa seguiria a mesma estrutura TDD detalhada.
