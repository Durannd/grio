# 🤖 GRIO SECURITY AUDIT - QUICK REFERENCE FOR AI AGENTS

**Status:** ⚠️ CRÍTICO - 6 Vulnerabilidades críticas identificadas  
**Data:** Abril 2025  
**Abordagem:** Implementação com Agentes de IA  
**Documentação Completa:** Ver `SECURITY_AUDIT_REPORT.md`

---

## 🤖 COMO USAR COM AGENTES DE IA

### Fluxo Recomendado

```
1. Escolha Vulnerabilidade (veja tabela abaixo)
   ↓
2. Lance Agente Apropriado (veja seção "Agentes")
   ↓
3. Revise Saída do Agente (code-review)
   ↓
4. Teste Incrementalmente
   ↓
5. Marque como Completo (SECURITY_FIX_CHECKLIST.md)
```

---

## 📊 RESUMO COM AGENTES - PRIORIDADE & TEMPO

| # | Título | Severidade | Agente Recomendado | Tempo | Complexidade |
|----|--------|-----------|-------------------|-------|--------------|
| 1 | Estado Auth | 🔴 | frontend-specialist | 1-2h | ALTA |
| 2 | Diagnóstico | 🔴 | backend-specialist | 1h | MÉDIA |
| 3 | Ownership | 🔴 | debugger + test-engineer | 1h | MÉDIA |
| 4 | XSS | 🔴 | security-auditor | 1h | MÉDIA |
| 5 | Token Revogação | 🔴 | backend-specialist | 2h | ALTA |
| 6 | CSRF | 🔴 | backend-specialist | 15m | BAIXA |
| 7 | JWT Expiração | 🟠 | backend-specialist | 30m | BAIXA |
| 8 | skill_id | 🟠 | backend-specialist | 1h | BAIXA |
| 9 | CORS | 🟠 | backend-specialist | 30m | BAIXA |
| 10 | Rate Limiting | 🟠 | backend-specialist | 1h | MÉDIA |
| 11 | Input Validation | 🟠 | backend-specialist | 1h | MÉDIA |

---

## 🔴 VULNERABILIDADES CRÍTICAS - PROMPTS PARA AGENTES

### #1: Estado Auth Inconsistente (FRONTEND)

**Agente:** `frontend-specialist`

```
"Implemente loading state no userStore para evitar race condition:

CONTEXTO:
- Arquivo: frontend/src/lib/stores/userStore.ts
- Problema: userStore carrega async, layout renderiza com estado null
- Resultado visual: Dashboard + Navbar desincronizados

RESTRIÇÕES (IMPORTANTE):
1. NÃO reescreva arquivo inteiro
2. Adicione apenas loading state
3. Preserve funcionalidade: subscribe, set, logout, load
4. Mantenha compatibilidade com +layout.svelte
5. Testes devem passar

IMPLEMENTAÇÃO:
1. Crie writable para loadingStore
2. Atualize loadUser() para gerenciar loading
3. Exporte loading no default object
4. NÃO delete código existente

Após: use frontend-specialist para atualizar +layout.svelte 
para renderizar <Skeleton /> durante loading"
```

**Validação:**
```bash
# Teste que layout aguarda antes de renderizar
# Verifique se navbar + dashboard estão sincronizados
# Confira que logout continua funcionando
```

---

### #2: Múltiplos Diagnósticos (BACKEND)

**Agente:** `backend-specialist`

```
"Implemente proteção contra múltiplos diagnósticos:

CONTEXTO:
- Arquivo: backend/api/v1/endpoints/assessment.py (POST /submit)
- Problema: User pode fazer diagnósticos infinitos
- Risco: Corrompe dados pedagógicos, gasta quota IA

RESTRIÇÕES:
1. Adicione flag is_diagnostic_in_progress em users table
2. Migrate: ALTER TABLE users ADD COLUMN is_diagnostic_in_progress BOOLEAN
3. NÃO apague código existente em submit_assessment
4. NÃO mude interface pública da API
5. Rate limiting por user_id, não IP

IMPLEMENTAÇÃO:
1. Crie migration do banco de dados
2. Adicione validação: if user.is_diagnostic_in_progress → 429
3. Set flag TRUE antes de processar
4. Set flag FALSE após completar ou erro
5. Testes para verificar 2º diagnóstico falha

Após: use test-engineer para testes de validação"
```

**Validação:**
```bash
# Tentar 2 diagnósticos consecutivos → 2º falha com 429
# Verificar que diagnóstico completo marca flag como false
# Testar erro durante diagnóstico marca flag como false
```

---

### #3: Falta de Ownership (TESTES)

**Agente:** `debugger` + `test-engineer`

```
"Implemente testes de IDOR para validação de ownership:

CONTEXTO:
- Arquivo: backend/api/v1/endpoints/assessment_report.py
- Problema: Verificar se validação de ownership funciona
- Método: GET /assessment-report/history/{attempt_id}

RESTRIÇÕES:
1. NÃO modifique código de produção (ainda)
2. Apenas adicione testes E2E
3. Use framework de testes existente

IMPLEMENTAÇÃO:
1. Crie teste: Login como user_id=1
2. Obtenha attempt_id de user_id=1
3. Tente acessar como user_id=2 com attempt_id de user_id=1
4. Esperado: 404 ou 403 (não 200)
5. Testar em TODOS endpoints com {id}

Após: se testes falharem, usar debugger para encontrar bug"
```

**Validação:**
```bash
# Executar testes E2E
# Tentar IDOR deve falhar (esperado)
# Acessar como user correto deve funcionar
```

---

### #4: XSS em Name Field (BACKEND + FRONTEND)

**Agente:** `backend-specialist` (backend) + `frontend-specialist` (frontend)

```
"Implemente validação de name field contra XSS:

CONTEXTO:
- Backend: backend/core/... (validação)
- Frontend: frontend/src/routes/+layout.svelte (rendering)
- Problema: Name field não sanitizado

RESTRIÇÕES:
1. Não delete código de rendering existente
2. Adicione validação no schema/models
3. Adicione regex pattern: ^[a-zA-Z0-9\s\-áéíóúãõ]{1,50}$
4. Frontend: Use DOMPurify se necessário
5. Preservar experiência do usuário

IMPLEMENTAÇÃO BACKEND:
1. Adicione regex validação em UserCreate schema
2. Rejeitar names com <, >, &, javascript
3. Retornar 400 com mensagem clara

IMPLEMENTAÇÃO FRONTEND:
1. Validar no formulário também (UX)
2. Sanitizar antes de renderizar com DOMPurify
3. Testes: Injetar HTML → deve falhar"
```

**Validação:**
```bash
# Tentar criar user com name contendo <img onerror=...>
# Esperado: 400 Bad Request
# Frontend: Sanitizar nome antes de renderizar
```

---

### #5: JWT sem Revogação (BACKEND + REDIS)

**Agente:** `backend-specialist`

```
"Implemente Token Blacklist com Redis:

CONTEXTO:
- Arquivo: backend/core/security.py + backend/api/v1/endpoints/auth.py
- Problema: JWT válido por 7 dias, logout não revoga
- Solução: Token Blacklist em Redis

RESTRIÇÕES:
1. NÃO delete código JWT existente
2. Adicione blacklist como camada extra
3. Preserve funcionalidade de logout existente
4. Não mude interface de autenticação pública
5. Manter compatibilidade com deploy existente

IMPLEMENTAÇÃO:
1. Criar core/redis_client.py com funções:
   - blacklist_token(token, expires_at)
   - is_token_blacklisted(jti)
2. Modificar logout() para chamar blacklist_token()
3. Modificar get_current_user() para checar blacklist
4. NÃO apagar delete_cookie (manter para UX)
5. Adicionar variáveis de ambiente para Redis

DEPOIS:
- Reduzir ACCESS_TOKEN_EXPIRE para 30min (separado)
- Implementar Refresh Tokens (separado)

Após: usar test-engineer para testes de revogação"
```

**Validação:**
```bash
# Login, obter token
# Logout
# Tentar usar token antigo → 401 (revogado)
```

---

### #6: CSRF (SameSite=lax) - QUICK WIN

**Agente:** `backend-specialist`

```
"Mudança de SameSite em cookies de autenticação:

CONTEXTO:
- Arquivo: backend/api/v1/endpoints/auth.py (linhas 44-50, 87-94)
- Problema: SameSite=lax permite CSRF em POST cross-site
- Solução: Mudar para SameSite=strict

RESTRIÇÕES:
1. Mudança mínima (1 linha x2)
2. NÃO toque em httponly ou secure
3. Preserve resto da lógica de cookies
4. Testar em desenvolvimento primeiro

IMPLEMENTAÇÃO:
1. Linha 49: samesite='lax' → samesite='strict'
2. Linha 93: samesite='lax' → samesite='strict'
3. Verificar secure=True em produção
4. Testes: Verificar que CSRF é bloqueado

ALERT: Se houver cross-site forms legítimas, usar CSRF tokens em vez disso"
```

**Validação:**
```bash
# Testar logout ainda funciona
# Testar login ainda funciona
# Tentar CSRF cross-site → bloqueado (esperado)
```

---

## 🟠 ALTAS - PROMPTS RÁPIDOS

### #7: JWT Expiração
```
"Reduzir ACCESS_TOKEN_EXPIRE_MINUTES de 7 dias para 30 minutos
Arquivo: backend/core/security.py linha 18
RESTRIÇÃO: 1 linha, teste logout"
```

### #8: skill_id Validation
```
"Adicionar regex validation para skill_id em assessment.py
Pattern: ^[A-Z]{2,3}(-[0-9]+)?$
Testar com skill_id inválido → 400"
```

### #9: CORS
```
"Adicionar Access-Control-Allow-Credentials: true em main.py
RESTRIÇÃO: Usar origem específica, não '*'
Testar requisição cross-origin com cookies"
```

### #10: Rate Limiting
```
"Mudar rate limiting de IP para user_id
Arquivo: backend/core/rate_limit.py
RESTRIÇÃO: Preservar rate limiting por IP para requests anônimas"
```

### #11: Input Validation
```
"Adicionar validação de area parameter (MT|CN|LC|CH)
Testes: Valores inválidos retornam 400"
```

---

## 🎯 DIA 1 COM AGENTES (3 horas)

```
1. #6 CSRF (15 min)
   └─ backend-specialist: "Mudar SameSite para strict"
   
2. #1 Auth Loading (1.5 horas)
   ├─ frontend-specialist: "Implementar loading state"
   └─ code-review: "Revisar mudanças"
   
3. #2 Diagnóstico (1 hora)
   ├─ backend-specialist: "Implementar flag"
   └─ test-engineer: "Escrever testes"
   
4. #3 Ownership (30 min)
   └─ test-engineer: "Testes de IDOR"
```

---

**Próximo:** Ver SECURITY_FIX_CHECKLIST.md para checklist com agentes

### #1: Estado Auth Inconsistente
- **Arquivo:** `frontend/src/lib/stores/userStore.ts:34-35`
- **Problema:** Race condition no carregamento de userStore
- **Sintoma:** Dashboard mostra nome + navbar "ENTRAR/CADASTRAR"
- **Fix:** Implementar loading state ou SvelteKit hooks
- **Tempo:** 1-2 horas

### #2: Múltiplos Diagnósticos sem Limite
- **Arquivo:** `backend/api/v1/endpoints/assessment.py:164-175`
- **Problema:** Qualquer user pode submeter diagnóstico infinitamente
- **Risco:** Corrompe dados pedagógicos, gasta quota IA
- **Fix:** Flag `is_diagnostic_in_progress` + validação backend
- **Tempo:** 1 hora

### #3: Falta de Validação de Ownership
- **Arquivo:** `backend/api/v1/endpoints/assessment_report.py:187-199`
- **Problema:** User pode acessar dados de outro user via IDOR
- **Risco:** Exposição de dados sensíveis
- **Fix:** Adicionar testes E2E + verificar em runtime
- **Tempo:** 1 hora

### #4: XSS em Name Field
- **Arquivo:** `frontend/src/routes/+layout.svelte:102, 109-110`
- **Problema:** HTML/JS não sanitizado em name field
- **Risco:** Cookie roubado via XSS
- **Fix:** Validar regex + DOMPurify
- **Tempo:** 1 hora

### #5: JWT sem Revogação (7 dias)
- **Arquivo:** `backend/core/security.py:18`
- **Problema:** Logout não revoga token, válido por 7 dias
- **Risco:** Token roubado = 7 dias de acesso
- **Fix:** Token Blacklist em Redis
- **Tempo:** 2 horas

### #6: CSRF Risk (SameSite=lax)
- **Arquivo:** `backend/api/v1/endpoints/auth.py:44-50, 87-94`
- **Problema:** Cookie permite POST cross-site
- **Risco:** Forçar ações maliciosas
- **Fix:** Mudar SameSite para strict (1 linha)
- **Tempo:** 5 minutos

---

## 🟠 VULNERABILIDADES ALTAS

1. **Expiração JWT muito longa** → Reduzir para 15-30 min
2. **Validação skill_id fraca** → Adicionar regex + whitelist
3. **CORS sem credenciais** → Access-Control-Allow-Credentials
4. **Rate limiting por IP** → Mudar para user_id
5. **Inputs sem validação** → Adicionar regex patterns

---

## 🟡 VULNERABILIDADES MÉDIAS

1. **Validação entrada fraca** → Regex patterns
2. **ENV vars sem força** → Aumentar para 64 chars

---

## ⚡ PLANO DE AÇÃO 3 DIAS

### DIA 1: Críticos Fáceis (3 horas)
- [ ] CSRF: SameSite=strict (5 min)
- [ ] Auth Loading: Implementar loading state (1 hora)
- [ ] Diagnóstico: Flag is_diagnostic_in_progress (1 hora)
- [ ] Ownership: Testes E2E (1 hora)

### DIA 2: Críticos Médios (4 horas)
- [ ] Token Blacklist em Redis (2 horas)
- [ ] Reduzir JWT para 15-30 min (30 min)
- [ ] Validar skill_id com regex (1 hora)
- [ ] CORS com credenciais (30 min)

### DIA 3: Críticos Complexos (4 horas)
- [ ] Sincronização Auth Frontend (2 horas)
- [ ] XSS + Sanitização (1 hora)
- [ ] Testes E2E segurança (1 hora)

---

## 🎯 CÓDIGO QUICK FIXES

### Fix #1: CSRF (5 min)
```python
# backend/api/v1/endpoints/auth.py
response.set_cookie(
    key="access_token",
    samesite="strict",  # ← Change from "lax"
    secure=True,
    httponly=True,
)
```

### Fix #2: Diagnóstico (30 min)
```python
# backend/api/v1/endpoints/assessment.py
@router.post("/submit")
def submit_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.is_diagnostic_in_progress:
        raise HTTPException(status_code=429, detail="Diagnostic already in progress")
    
    # Mark as in progress
    current_user.is_diagnostic_in_progress = True
    db.commit()
    
    try:
        result = process_assessment_submission(db, submission)
        current_user.is_diagnostic_in_progress = False
        current_user.is_diagnostic_completed = True
        db.commit()
        return result
    except Exception as e:
        current_user.is_diagnostic_in_progress = False
        db.commit()
        raise
```

### Fix #3: Loading State (1 hour)
```typescript
// frontend/src/lib/stores/userStore.ts
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

export default {
  subscribe: userStore.subscribe,
  loading: { subscribe: loadingStore.subscribe },
  load: loadUser,
};
```

```svelte
<!-- frontend/src/routes/+layout.svelte -->
<script>
  import { page } from '$app/stores';
  import userStore from '$lib/stores/userStore';
  
  let loading = true;
  userStore.loading?.subscribe(val => loading = val);
</script>

{#if loading}
  <nav class="glass-nav">
    <div class="nav-content container">
      <a href="/" class="brand">
        <img src="/grio-logo.png" alt="Logotipo Griô" />
      </a>
      <div class="skeleton"></div>
    </div>
  </nav>
{:else}
  <!-- Renderizar navbar normalmente -->
{/if}
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Semana 1
- [ ] Mudar SameSite para strict
- [ ] Implementar loading state
- [ ] Adicionar is_diagnostic_in_progress flag
- [ ] Adicionar testes de ownership
- [ ] Implementar Token Blacklist
- [ ] Reduzir JWT expiração

### Semana 2
- [ ] Validar skill_id com regex
- [ ] CORS com credenciais
- [ ] Sanitizar name field
- [ ] Rate limiting por user
- [ ] Testes E2E segurança

### Semana 3
- [ ] Sincronização Auth completa
- [ ] Validação entrada completa
- [ ] Re-auditoria de segurança
- [ ] Documentar mudanças

---

## 🔗 RECURSOS

- **Documentação Completa:** `SECURITY_AUDIT_REPORT.md`
- **Banco de Dados Findings:** SQL table `security_findings`
- **OWASP A01 (Broken Access Control):** https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- **OWASP A03 (Injection):** https://owasp.org/Top10/A03_2021-Injection/
- **OWASP A06 (Insecure Design):** https://owasp.org/Top10/A06_2021-Insecure_Design/

---

**Última Atualização:** Abril 2025  
**Próxima Review:** Após implementação de todos os fixes críticos
