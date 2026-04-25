<div align="center">

# Griô

### Conhecimento é herança coletiva, não mercadoria.

*Knowledge is a collective heritage, not a commodity.*

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)](https://github.com/Durannd/grio)
[![Stack](https://img.shields.io/badge/stack-SvelteKit%20%7C%20FastAPI%20%7C%20Neo4j-blueviolet?style=for-the-badge)](https://github.com/Durannd/grio)

</div>

---

> 💡 **Documentação Técnica**: Para detalhes aprofundados sobre a arquitetura de grafos, embeddings e o motor de diagnóstico, acesse as [Especificações Técnicas](TECHNICAL_SPECIFICATIONS.md).

<details open>
<summary><strong>🇧🇷 Português</strong></summary>

<br>

## O Problema

No Brasil, a preparação para o vestibular é profundamente desigual. Cursinhos de qualidade custam entre R$300 e R$3.000/mês, criando uma barreira que perpetua um ciclo vicioso: quem tem dinheiro entra nas melhores universidades públicas (gratuitas), e quem não tem fica de fora.

O **Griô** existe para quebrar esse ciclo.

> O nome vem da tradição africana do **Griô (griot)** — o guardião que transmite conhecimento de geração em geração, sem cobrar nada, porque saber pertence a todos.

## A Proposta

Uma plataforma **gratuita e inteligente** que oferece ao estudante de baixa renda a mesma qualidade de preparação de um cursinho de elite — usando **Inteligência Artificial** e um **Banco de Dados em Grafo** como diferenciais.

### Pilares

| | Pilar | Descrição |
|---|---|---|
| 🤖 | **IA como Tutora** | Assistente que entende o nível do aluno, tira dúvidas e personaliza o estudo |
| 🧠 | **Grafo de Conhecimento** | Rede que conecta conceitos, exercícios e perfil do aluno, identificando lacunas |
| 🔥 | **Hábito sobre Intensidade** | Gamificação focada em consistência diária, não picos esporádicos |
| 📱 | **Mobile-First** | Projetado para funcionar em celulares com dados limitados |

## MVP: Matemática

O primeiro passo é construir **todas as funcionalidades** para uma única matéria — Matemática — validando o modelo completo antes de expandir.

**O MVP inclui:**
- 📝 Prova de nivelamento para mapear o nível do aluno
- 🗺️ Trilha de aprendizado personalizada (Aprenda → Pratique → Domine)
- 💬 Chat com IA contextual para tirar dúvidas
- 🏆 Sistema de streaks e conquistas
- 📚 Banco de questões de vestibulares anteriores (ENEM, FUVEST, etc.)

## Stack Tecnológica

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Frontend | **SvelteKit** | Performance e leveza mobile |
| Backend | **Python + FastAPI** | Ecossistema de IA maduro |
| Banco Relacional | **PostgreSQL** | Dados de usuários, autenticação e histórico imutável de avaliações |
| Banco em Grafo | **Neo4j** | Grafo de conhecimento e proficiência (estado cognitivo atual) |
| IA | **Gemini API** | Tutor inteligente |

## Roadmap

```
Fase 1 ▸ Beta Fechado     MVP de Matemática para grupo restrito          3-4 meses
Fase 2 ▸ Beta Aberto      Lançamento público de Matemática              +2-3 meses
Fase 3 ▸ Expansão         Física, Química e correção de redação por IA  +6 meses
```

## Licença

Este projeto é de **código-fonte visível** (source-available), mas **não é open-source**.
Todos os direitos são reservados. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  <em>Na tradição africana, o Griô não é dono do conhecimento.<br>Ele é um guardião temporário. O conhecimento pertence a todos.</em>
</p>

</details>

---

<details>
<summary><strong>🇺🇸 English</strong></summary>

<br>

## The Problem

In Brazil, preparation for university entrance exams (_vestibular_) is deeply unequal. Quality prep courses cost between $60–$600/month, creating a barrier that perpetuates a vicious cycle: those with money get into the best public (free) universities, while those without are left behind.

**Griô** exists to break this cycle.

> The name comes from the African **Griot** tradition — the keeper who passes down knowledge from generation to generation, freely, because wisdom belongs to everyone.

## The Vision

A **free and intelligent** platform that gives low-income students the same quality of preparation as elite prep courses — using **Artificial Intelligence** and a **Graph Database** as core differentiators.

### Core Principles

| | Principle | Description |
|---|---|---|
| 🤖 | **AI as a Tutor** | Assistant that understands the student's level, answers questions, and personalizes learning |
| 🧠 | **Knowledge Graph** | Network connecting concepts, exercises, and student profiles, identifying gaps |
| 🔥 | **Habit over Intensity** | Gamification focused on daily consistency, not sporadic bursts |
| 📱 | **Mobile-First** | Designed to work on phones with limited data plans |

## MVP: Mathematics

The first step is building **all features** for a single subject — Mathematics — validating the complete model before expanding.

**The MVP includes:**
- 📝 Placement test to map the student's current level
- 🗺️ Personalized learning path (Learn → Practice → Master)
- 💬 Context-aware AI chat for real-time help
- 🏆 Streak and achievement system
- 📚 Question bank from past national exams (ENEM, FUVEST, etc.)

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | **SvelteKit** | Mobile performance and lightweight bundle |
| Backend | **Python + FastAPI** | Mature AI ecosystem |
| Relational DB | **PostgreSQL** | User data and authentication |
| Graph DB | **Neo4j** | Knowledge graph and student proficiency |
| AI | **Gemini API** | Intelligent tutor |

## Roadmap

```
Phase 1 ▸ Closed Beta     Mathematics MVP for a small group             3-4 months
Phase 2 ▸ Open Beta       Public launch of Mathematics                  +2-3 months
Phase 3 ▸ Expansion       Physics, Chemistry, and AI essay grading      +6 months
```

## License

This project is **source-available** but **not open-source**.
All rights reserved. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <em>In the African tradition, the Griot does not own knowledge.<br>They are a temporary guardian. Knowledge belongs to everyone.</em>
</p>

</details>
