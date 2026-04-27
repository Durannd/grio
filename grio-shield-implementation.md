# Plano de Implementação: Grio Shield 🛡️

## Objetivo
Proteger a Propriedade Intelectual (IP) do projeto, ofuscar a lógica do grafo pedagógico e fechar brechas de segurança nos endpoints.

## 1. Segurança de Endpoints (Urgente)
- [ ] **`backend/api/v1/endpoints/concepts.py`**: Adicionar dependência de autenticação no POST.
- [ ] **Limpeza de Rotas**: Verificar se há outros endpoints de "escrita" (POST/PUT/DELETE) expostos sem necessidade.

## 2. Proteção do "Segredo de Estado" (Taxonomia)
- [ ] **Ofuscação de IDs**: Criar um utilitário `core/translator.py` que mascara os códigos ENEM (ex: `MT_C1_H1` -> `SKL-A71B`).
- [ ] **Refatoração de Responses**: Atualizar os roteadores de `learning_path` e `study_plan` para usar os IDs mascarados.
- [ ] **Proteção de Prompt**: Ajustar o prompt do Gemini para não descrever a lógica de inferência de forma que possa ser logada ou interceptada facilmente.

## 3. Branding e UX (Sobre Nós)
- [ ] **`frontend/src/routes/sobre/+page.svelte`**: Remover menções a Neo4j, FastAPI e SvelteKit. Substituir por termos focados em benefícios (ex: "Arquitetura de Conhecimento não-linear").

## 4. Auditoria de Arquivos
- [ ] **`.env`**: Garantir que não está sendo servido ou acessível via web.
- [ ] **Scripts**: Mover a pasta `backend/scripts` para um local que não possa ser mapeado via URL.

## Critérios de Sucesso
- Nenhum endpoint de dados sensíveis acessível sem JWT.
- IDs da matriz ENEM não visíveis no console do desenvolvedor no frontend.
- Documentação pública e site focados no "quê" e não no "como".
