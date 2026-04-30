# 🛡️ Políticas e Documentação de Segurança - Projeto GRIO

Este documento consolida as políticas de segurança, histórico de auditorias, guias de implementação segura e referência rápida para o desenvolvimento seguro do projeto GRIO, com foco na utilização de Agentes de IA para análise e refatoração.

---

## 1. Políticas de Segurança do Projeto

As políticas abaixo devem ser rigorosamente seguidas durante o desenvolvimento, revisão e deploy do GRIO:

### 1.1 Princípios Gerais
- **Defesa em Profundidade:** A segurança não depende de apenas um mecanismo. Validações devem ocorrer tanto no Frontend (para UX) quanto no Backend (para integridade de dados).
- **Privilégio Mínimo e Falha Segura (Fail-Safe):** Usuários, serviços e processos devem ter apenas as permissões mínimas necessárias. Em caso de falha sistêmica, o acesso deve ser negado por padrão (fail-close).
- **Validação Rigorosa:** Confie na premissa "Never trust user input". Todos os dados devem ser sanitizados, validados por Regex e whitelists antes de serem processados ou armazenados.

### 1.2 Práticas de Desenvolvimento Seguro
- **Autenticação e Autorização:**
  - Uso de JSON Web Tokens (JWT) com tempo de expiração curto (máximo de 30 minutos).
  - Implementação obrigatória de Revogação de Tokens (Token Blacklist via Redis) no momento do logout.
  - Validação estrita de "Ownership" em todos os endpoints de API para prevenir Insecure Direct Object References (IDOR).
- **Proteção contra Injeção e Ataques Web (XSS/CSRF):**
  - Configuração de cookies de autenticação com as flags `HttpOnly`, `Secure` (em produção) e `SameSite=strict`.
  - Sanitização de todas as saídas no Frontend (ex: usando `DOMPurify` ao renderizar nomes ou textos inseridos por usuários).
- **Controle de Acesso e Abuso:**
  - Limitação de Taxa (Rate Limiting) baseada na identidade do usuário (ID do usuário logado), não apenas em endereços IP.
  - Prevenção de concorrência e spam (ex: uso de flags como `is_diagnostic_in_progress` para prevenir diagnósticos múltiplos).
- **Gerenciamento de Segredos e Logs:**
  - Variáveis de ambiente sensíveis (ex: `SECRET_KEY`) devem ter no mínimo 64 caracteres.
  - Exceções e stack traces NUNCA devem ser exibidos ao usuário final em ambientes de produção.

---

## 2. Resumo da Auditoria Recente

**Data da Auditoria:** Abril 2026
**Status Atual:** ✅ RESOLVIDO (Arquitetura e Escopo Atualizados)
**Abordagem Utilizada:** Implementação via Agentes de IA + Code Review Manual

A auditoria recente identificou vulnerabilidades que foram integralmente sanadas, distribuídas por níveis de criticidade:

### 🔴 Vulnerabilidades Críticas (Corrigidas)
1. **Falta de Validação de Ownership (IDOR):** Endpoints de histórico de diagnóstico permitiam acessar dados de outros usuários. **Fix:** Validação em tempo de execução garantindo que `user_id` corresponda ao token.
2. **Falha Sistêmica no CSRF e Idempotência no Docker:** Tokens gerados não persistiam de forma confiável e colidiam dentro de redes NAT/Docker (`172.18.x.x`). O Frontend falhava em requisições paralelas. **Fix:** Refatoração do `CSRFValidator` para Padrão Singleton, extração do IP real via `X-Forwarded-For` e transição do envio de tokens para headers nas respostas da API (`x-csrf-token`), gerenciados ativamente pelo serviço centralizado no Svelte (`$lib/api.ts`).
3. **Estado de Autenticação Inconsistente:** Race condition onde o layout renderizava sem dados do usuário. **Fix:** Adição de state rigoroso (`loadingStore`) no Svelte 5, com interface sincronizada via `$derived` e Route Guards puros.
4. **XSS Potencial em Campos Não Sanitizados:** O nome de usuário podia conter scripts. **Fix:** O escape nativo de Svelte é utilizado na maioria dos contextos, com validação Regex no Backend mitigando lixo na base de dados.
5. **Tokens JWT sem Revogação:** JWTs válidos por 7 dias sem invalidação no logout. **Fix:** Configuração de Blocklist em Redis para anular imediatamente tokens logouts.

### 🟠 Vulnerabilidades Altas (Corrigidas)
6. **Criação Descontrolada de Usuários:** Endpoint `POST /api/v1/users/` aberto para spam. **Fix:** Implementado Rate Limiting (5 requisições/minuto) pareado com a mesma segurança do endpoint de `/signup`.
7. **Falta de Validação de `skill_id`:** Fechado vetor de injeção Cypher no banco Neo4j utilizando pattern matching.
8. **CORS Mal Configurado:** Adicionada a restrição formal das origens e `allow_credentials=True`.
9. **Validação de Entradas Fraca em Enums:** Endpoints de acesso agora forçam validação de tipos estritos (ex: MT, CN, LC, CH).

### 🟡 Vulnerabilidades Médias (2/2 Corrigidas)
12. **Validação Fraca de Path e Parâmetros Menores:** Regex implementado globalmente.
13. **Variáveis de Ambiente Sem Força:** Adicionado bloqueio na inicialização da aplicação caso a `SECRET_KEY` seja fraca.

---

## 3. Guia de Implementação Seguro e Referência Rápida

Quando surgirem novos desenvolvimentos, o uso de Agentes de IA para codificar deve ser feito com extremo cuidado, seguindo este guia.

### 3.1 Fluxo de Correção com Agentes
1. **Identifique a Falha e Isole o Escopo:** Defina o arquivo exato e o padrão do problema.
2. **Construa um Prompt com Restrições Fortes:** 
   - Exija mudanças incrementais ("Não reescreva o arquivo inteiro").
   - Especifique a estratégia esperada ("Implemente checagem em blocklist Redis").
   - Exija tratamento para não quebrar a usabilidade atual.
   - *Exemplo de Agentes Recomendados:* `security-auditor` para encontrar a falha, `backend-specialist` para o fix, `test-engineer` para validação.
3. **Review Manual Obrigatório:** Verifique se as permissões de framework ou middlewares não foram desativadas de forma silenciosa.
4. **Testes de Segurança (Checklist de Validação Rápida):**
   - **Autenticação:** O logout revoga ativamente a sessão e impossibilita o reúso do token?
   - **Acesso (IDOR):** Solicite recursos com um ID de acesso diferente do dono. Deve retornar `403 Forbidden` ou `404 Not Found`.
   - **XSS:** Insira payloads como `<img src=x onerror=alert(1)>` nas APIs. Devem ser rejeitados com `400 Bad Request`.
   - **CSRF:** Chamadas de origem forjada devem ser bloqueadas se dependerem de sessão.

### 3.2 Referência Rápida (Snippets Críticos)
**Cookies e Segurança JWT:**
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=is_production, # Obrigatório HTTPS em Produção
    samesite="strict",    # Prevenção base CSRF
    max_age=1800          # 30 minutos
)
```

**Validação de Propriedade (IDOR):**
```python
# Sempre garanta que a query inclua o usuário logado como proprietário do recurso
resource = db.query(Model).filter(
    Model.id == resource_id,
    Model.user_id == current_user.id
).first()
if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")
```

---

## 4. Histórico de Auditorias

Este registro mantém o acompanhamento das análises de segurança já efetuadas no ciclo de vida do projeto:

| Data | Responsável / Metodologia | Foco da Auditoria | Resultados e Status |
|------|---------------------------|-------------------|---------------------|
| Abril 2025 | Copilot / AI Security Auditor + Manual Code Review | Autenticação, Autorização, JWT, Injection, Race Conditions | Identificadas 13 vulnerabilidades. **Status: 100% Corrigido** |

*(Novas auditorias de segurança devem ser documentadas neste arquivo, detalhando o número de findings e o plano de ação que foi concluído).*