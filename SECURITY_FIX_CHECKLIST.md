# 🤖 SECURITY AUDIT - FIX CHECKLIST WITH AI AGENTS

**Generated:** Abril 2025  
**Total Items:** 13 vulnerabilidades  
**Status:** 0/13 Fixed (0%)  
**Approach:** Implementação com Agentes de IA

---

## 🎯 WORKFLOW COM AGENTES

```
Para cada vulnerabilidade:
1. Copie o prompt da seção "Agente"
2. Lance o agente apropriado (veja tabela abaixo)
3. Cole o prompt completo
4. Revise saída do agente
5. Execute testes de validação
6. Marque checkbox como ✅ completo
```

---

## 📋 TABELA DE AGENTES

| # | Problema | Agente | Tempo | Status |
|----|----------|--------|-------|--------|
| 1 | Estado Auth | frontend-specialist | 1-2h | ⏳ |
| 2 | Diagnóstico | backend-specialist | 1h | ⏳ |
| 3 | Ownership | test-engineer | 1h | ⏳ |
| 4 | XSS | security-auditor | 1h | ⏳ |
| 5 | Token Revogação | backend-specialist | 2h | ⏳ |
| 6 | CSRF | backend-specialist | 15m | ⏳ |
| 7 | JWT Expiração | backend-specialist | 30m | ⏳ |
| 8 | skill_id | backend-specialist | 1h | ⏳ |
| 9 | CORS | backend-specialist | 30m | ⏳ |
| 10 | Rate Limiting | backend-specialist | 1h | ⏳ |
| 11 | Input Validation | backend-specialist | 1h | ⏳ |

---

## 🔴 CRÍTICAS (6/6 Pendentes)

### #1 - Estado Auth Inconsistente (CVSS 8.0)
**Agente:** `frontend-specialist`

**Prompt para colar:**
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

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `frontend-specialist`
- [ ] Revise saída com: `code-review`
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# Teste que layout aguarda antes de renderizar
# Verifique se navbar + dashboard estão sincronizados
# Confira que logout continua funcionando
# Teste em todos navegadores (Chrome, Firefox, Safari)
```

**Evidence:** Dashboard mostra nome + navbar "ENTRAR/CADASTRAR"

---

### #2 - Múltiplos Diagnósticos sem Limite (CVSS 8.8)
**Agente:** `backend-specialist`

**Prompt para colar:**
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

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `backend-specialist`
- [ ] Revise saída
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# Tentar 2 diagnósticos consecutivos → 2º falha com 429
# Verificar que diagnóstico completo marca flag como false
# Testar erro durante diagnóstico marca flag como false
# Teste rate limiting: requisições rápidas do mesmo user
```

---

### #3 - Falta de Validação de Ownership (CVSS 9.1)
**Agente:** `test-engineer`

**Prompt para colar:**
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

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `test-engineer`
- [ ] Revise testes escritos
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# Executar: pytest tests/test_idor.py -v
# Tentativa IDOR deve FALHAR (401/403/404)
# Acessar como user correto deve PASSAR (200)
# Testar em TODOS endpoints: /history, /report, /results
```

---

### #4 - XSS em Name Field (CVSS 8.6)
**Agente:** `security-auditor`

**Prompt para colar:**
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

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `security-auditor`
- [ ] Revise implementação
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# Backend: POST /auth/register com name="<img onerror=alert()>"
# Esperado: 400 Bad Request
# Frontend: Tentar injetar na UI
# Verificar sanitização no inspector (sem tags HTML)
```

---

### #5 - JWT sem Revogação (CVSS 8.2)
**Agente:** `backend-specialist`

**Prompt para colar:**
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

DEPOIS (SEPARADO):
- Reduzir ACCESS_TOKEN_EXPIRE para 30min
- Implementar Refresh Tokens

Após: usar test-engineer para testes de revogação"
```

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `backend-specialist`
- [ ] Revise implementação Redis
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# 1. Login: POST /auth/login → obter token
# 2. Logout: POST /auth/logout com token
# 3. Tentar usar token antigo: GET /assessment com token antigo
# Esperado: 401 Unauthorized (revogado)
```

---

### #6 - CSRF (SameSite=lax) - QUICK WIN (CVSS 8.1)
**Agente:** `backend-specialist`

**Prompt para colar:**
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

**Tasks:**
- [ ] Copie prompt acima
- [ ] Lance agente: `backend-specialist`
- [ ] Revise mudança (2 linhas apenas)
- [ ] Execute testes (veja abaixo)
- [ ] Marque como ✅ completo

**Testes de Validação:**
```bash
# Testar logout ainda funciona: POST /auth/logout
# Testar login ainda funciona: POST /auth/login
# CSRF test: Tentar POST de cross-site → bloqueado
# Verificar em navegador: DevTools → Cookies → SameSite
```

---

## 🟠 ALTAS (5/5 Pendentes)

### #7 - JWT Expiração Longa (CVSS 7.2)
**Agente:** `backend-specialist`

**Prompt:**
```
"Reduzir expiração de JWT:
Arquivo: backend/core/security.py
Mudança: ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60
Para: ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESTRIÇÃO: 1 linha, teste logout"
```

**Tasks:**
- [ ] Lance agente
- [ ] Revise mudança (1 linha)
- [ ] Teste: logout + login
- [ ] ✅ Completo

**Validação:**
```bash
# Esperar 31+ minutos, token deve expirar
# Logout + login deve gerar novo token
```

---

### #8 - skill_id sem Validação (CVSS 6.1)
**Agente:** `backend-specialist`

**Prompt:**
```
"Adicionar regex validation para skill_id:
Arquivo: backend/api/v1/endpoints/assessment.py
Pattern: ^[A-Z]{2,3}(-[0-9]+)?$
Teste: skill_id inválido → 400 Bad Request"
```

**Tasks:**
- [ ] Lance agente
- [ ] Revise validação
- [ ] Teste com valores inválidos
- [ ] ✅ Completo

---

### #9 - CORS credentials (CVSS 6.8)
**Agente:** `backend-specialist`

**Prompt:**
```
"Adicionar Access-Control-Allow-Credentials:
Arquivo: backend/main.py
Mudança: add_middleware(CORSMiddleware, ...)
Allow: allow_credentials=True, origins=['https://seu-dominio.com']
RESTRIÇÃO: Usar origem específica, não '*'"
```

**Tasks:**
- [ ] Lance agente
- [ ] Teste cross-origin com cookies
- [ ] ✅ Completo

---

### #10 - Rate Limiting por IP (CVSS 6.9)
**Agente:** `backend-specialist`

**Prompt:**
```
"Implementar rate limiting por user_id:
Arquivo: backend/core/rate_limit.py
Preservar: Rate limiting por IP para requests anônimas
Novo: Rate limiting por user_id para autenticados
Teste: Mesmo IP, 2 users → limites independentes"
```

**Tasks:**
- [ ] Lance agente
- [ ] Teste: múltiplos users mesma IP
- [ ] ✅ Completo

---

### #11 - Input Validation (CVSS 6.5)
**Agente:** `backend-specialist`

**Prompt:**
```
"Adicionar validação de area parameter:
Arquivo: backend/api/v1/endpoints/assessment.py
Valores válidos: MT|CN|LC|CH
Inválidos: Retornar 400
Testes: Cada valor inválido → 400"
```

**Tasks:**
- [ ] Lance agente
- [ ] Teste valores inválidos
- [ ] ✅ Completo

---

## 🟡 MÉDIAS (2/2 Pendentes)

### #12 - Informação Sensível em Errors
- [ ] Remover stack traces em produção
- [ ] Logar em arquivo, não expor user

### #13 - Logs de Segurança
- [ ] Implementar audit log para login/logout
- [ ] Registrar failed attempts

---

## 📊 PROGRESSO

```
🔴 Críticas: ████░░░░░░░░ 0/6 (0%)
🟠 Altas:    ████░░░░░░░░ 0/5 (0%)
🟡 Médias:   ████░░░░░░░░ 0/2 (0%)
━━━━━━━━━━━━━━━━━━━━━━━━
Total:       0/13 (0%)
```

---

## ✅ PRÓXIMAS AÇÕES

1. Escolha vulnerabilidade da tabela acima
2. Copie o **Prompt para colar** da seção
3. Lance o **Agente** recomendado
4. Revise saída
5. Execute **Testes de Validação**
6. Marque checkbox como ✅

**Dia 1 Goal:** Completar #6, #1, #2, #3 (3 horas)
- [ ] Backend: Rejeitar names com HTML
- [ ] Frontend: Importar DOMPurify
- [ ] Frontend: Sanitizar name antes de renderizar
- [ ] Testes: Injetar `<img onerror=alert('XSS')>`
- [ ] Verificar em avatar + user-name + user-email

**Fix Time:** 1 hora

---

### #5 - JWT sem Revogação (CVSS 7.5)
**Arquivo:** `backend/core/security.py` + `backend/api/v1/endpoints/auth.py`

- [ ] Instalar Redis
- [ ] Criar arquivo `backend/core/redis_client.py`
- [ ] Implementar `blacklist_token()` function
- [ ] Implementar `is_token_blacklisted()` function
- [ ] Modificar `logout()` para adicionar token à blacklist
- [ ] Modificar `get_current_user()` para verificar blacklist
- [ ] Reduzir `ACCESS_TOKEN_EXPIRE_MINUTES` para 30
- [ ] Implementar Refresh Tokens (expiração 7 dias)
- [ ] Testes: Logout deve invalidar token
- [ ] Testes: Token expirado deve falhar

**Fix Time:** 2 horas

---

### #6 - CSRF Risk (SameSite=lax) (CVSS 7.0)
**Arquivo:** `backend/api/v1/endpoints/auth.py`

- [ ] Linha 49: Mudar `samesite="lax"` para `samesite="strict"`
- [ ] Linha 93: Mudar `samesite="lax"` para `samesite="strict"`
- [ ] Verificar em produção: `secure=True`
- [ ] Testes: Tentar POST cross-site
- [ ] Testes: Verificar se CSRF é bloqueado

**Fix Time:** 5 minutos + testing

---

## 🟠 ALTAS (5/5 Pendentes)

### #7 - Expiração JWT muito Longa (CVSS 7.5)
**Arquivo:** `backend/core/security.py`

- [ ] Reduzir de 7 dias para 30 minutos
- [ ] Implementar Refresh Token (7 dias)
- [ ] Frontend: Detectar token expirado (401)
- [ ] Frontend: Automaticamente atualizar token
- [ ] Testes: Token expirado retorna 401

**Fix Time:** 2 horas

---

### #8 - Validação skill_id Fraca (CVSS 6.5)
**Arquivo:** `backend/api/v1/endpoints/assessment.py`

- [ ] Adicionar regex validation
  ```python
  SKILL_ID_PATTERN = re.compile(r'^[A-Z]{2,3}(-[0-9]+)?$')
  ```
- [ ] Criar whitelist de skills válidos
- [ ] Validar em `GET /assessment/practice/{skill_id}`
- [ ] Validar em `GET /assessment/diagnostico/{area}`
- [ ] Retornar 400 para skill_id inválido
- [ ] Testes: Tentar skill_id com injection

**Fix Time:** 1 hora

---

### #9 - CORS sem Credenciais (CVSS 6.0)
**Arquivo:** `backend/main.py`

- [ ] Verificar configuração CORS atual
- [ ] Adicionar `allow_credentials=True`
- [ ] Especificar `allow_origins` (não usar *)
- [ ] Testar requisições cross-origin com cookies
- [ ] Verificar em produção

**Fix Time:** 30 minutos

---

### #10 - Rate Limiting por IP (CVSS 6.5)
**Arquivo:** `backend/core/rate_limit.py`

- [ ] Mudar key_func de IP para user_id
- [ ] Implementar por user autenticado
- [ ] Máximo 1 diagnóstico por minuto
- [ ] Máximo 10 submissions por hora
- [ ] Testes: Múltiplas requisições como mesmo user

**Fix Time:** 1 hora

---

### #11 - Inputs sem Validação (CVSS 5.0)
**Arquivo:** `backend/api/v1/endpoints/assessment.py`

- [ ] Validar `area` parameter (MT|CN|LC|CH)
- [ ] Validar `skill_id` format
- [ ] Adicionar regex patterns
- [ ] Testes: Valores inválidos retornam 400

**Fix Time:** 1 hora

---

## 🟡 MÉDIAS (2/2 Pendentes)

### #12 - Validação Entrada Fraca (CVSS 5.5)
**Arquivo:** `backend/api/v1/endpoints/`

- [ ] Adicionar regex patterns em todos endpoints
- [ ] Documentar validação esperada
- [ ] Testes: Invalid input retorna erro

**Fix Time:** 1 hora

---

### #13 - ENV Vars sem Força (CVSS 4.5)
**Arquivo:** `backend/core/security.py`

- [ ] Aumentar `SECRET_KEY` mínimo para 64 chars
- [ ] Documentar requisitos de env vars
- [ ] Verificar em CI/CD

**Fix Time:** 30 minutos

---

## 📊 PROGRESSO

### Status Geral
- 🔴 CRÍTICAS: 0/6 Fixadas (0%)
- 🟠 ALTAS: 0/5 Fixadas (0%)
- 🟡 MÉDIAS: 0/2 Fixadas (0%)
- **TOTAL: 0/13 Fixadas (0%)**

### Timeline Proposto
- **Dia 1 (CRÍTICAS FÁCEIS):** #1, #6, #2 = 3 itens
- **Dia 2 (CRÍTICAS MÉDIAS):** #5, #3, #4 = 3 itens
- **Dia 3+ (ALTAS/MÉDIAS):** #7-13 = 7 itens

---

## 🧪 TESTES DE VALIDAÇÃO

Para cada fix, execute os seguintes testes:

### Teste IDOR (Ownership Validation)
```bash
# Como user_id=1
TOKEN=$(curl ... /auth/login)

# Tentar acessar attempt de user_id=2
curl -H "Cookie: access_token=$TOKEN" \
  https://grio.com/api/v1/assessment-report/history/99999

# Esperado: 404 ou 403 (not found/forbidden)
# Não esperado: 200 (acesso concedido)
```

### Teste Múltiplos Diagnósticos
```bash
# Enviar 2 diagnósticos consecutivos
curl -X POST https://grio.com/api/v1/assessment/submit -d '{...}'
curl -X POST https://grio.com/api/v1/assessment/submit -d '{...}'

# Esperado: 2º retorna 429 ou 403
# Não esperado: 2º retorna 200
```

### Teste CSRF
```bash
# Em domínio externo
<form method="POST" action="https://grio.com/api/v1/assessment/submit">
  <input type="hidden" name="answers" value="[...]">
</form>
<script>document.querySelector('form').submit()</script>

# Esperado: 403 (CSRF bloqueado)
# Não esperado: 200 (CSRF permitido)
```

### Teste XSS
```bash
# Injetar em name field
name = "<img src=x onerror='alert(\"XSS\")'>"

# Esperado: Rejeitado com erro 400
# Não esperado: Armazenado e renderizado
```

### Teste Token Revocation
```bash
# 1. Login
TOKEN=$(curl ... /auth/login)

# 2. Logout (deve revogar)
curl -X POST ... /auth/logout

# 3. Tentar usar token antigo
curl -H "Cookie: access_token=$TOKEN" ...

# Esperado: 401 (unauthorized)
# Não esperado: 200 (still authorized)
```

---

## 📝 NOTAS IMPORTANTES

- **Não skip testes:** Cada fix deve ser testado antes de marcar como completo
- **Documentar mudanças:** Adicionar comentários no código explicando fix
- **Atualizar ENV vars:** Modificar `.env.example` com novos requirements
- **Notificar time:** Comunicar quando fixes críticas estiverem prontas
- **Re-auditoria:** Após todos os fixes, re-executar auditoria completa

---

## 🎯 OBJETIVO FINAL

✅ **Todas as 13 vulnerabilidades fixadas**  
✅ **Todos os testes passando**  
✅ **Re-auditoria de segurança aprovada**  
✅ **Documentação atualizada**  
✅ **Code review completado**

---

**Checklist Version:** 1.0  
**Last Updated:** Abril 2025  
**Next Review:** Após cada fix crítica
