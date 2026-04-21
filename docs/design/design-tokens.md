# Griô — Design Tokens & Guia Visual

> **Este arquivo é a fonte de verdade para cores, tipografia e espaçamento do projeto Griô.**
> Toda decisão de frontend deve seguir estes tokens.

---

## 1. Paleta de Cores

### 1.1. Cores Principais

| Token                | Hex       | HSL                  | Uso                                              |
|----------------------|-----------|----------------------|--------------------------------------------------|
| `--color-primary`    | `#D4940A` | `hsl(40, 91%, 43%)`  | Ações principais, botões CTA, destaques          |
| `--color-primary-light` | `#F2B830` | `hsl(43, 89%, 57%)` | Hover de botões, badges, notificações            |
| `--color-primary-dark`  | `#A67208` | `hsl(40, 91%, 34%)` | Botões pressionados, bordas ativas               |

### 1.2. Cores Secundárias

| Token                   | Hex       | HSL                  | Uso                                            |
|-------------------------|-----------|----------------------|------------------------------------------------|
| `--color-secondary`     | `#2D1B69` | `hsl(258, 59%, 26%)` | Headers, sidebar, elementos de destaque        |
| `--color-secondary-light` | `#4A3399` | `hsl(258, 50%, 40%)` | Hover de elementos secundários                |
| `--color-secondary-dark`  | `#1A0F3D` | `hsl(258, 62%, 15%)` | Fundo de modais, overlays                     |

### 1.3. Cores de Acento

| Token               | Hex       | HSL                  | Uso                                              |
|----------------------|-----------|----------------------|--------------------------------------------------|
| `--color-accent`     | `#C45A3C` | `hsl(13, 53%, 50%)`  | Alertas, streaks, gamificação, badges quentes     |
| `--color-accent-light` | `#E07A5F` | `hsl(13, 68%, 62%)` | Hover de acentos, ícones                         |
| `--color-accent-dark`  | `#9A3F28` | `hsl(13, 58%, 38%)` | Bordas de alerta                                 |

### 1.4. Cores Semânticas (Feedback)

| Token              | Hex       | Uso                                           |
|--------------------|-----------|-----------------------------------------------|
| `--color-success`  | `#2D9F5A` | Resposta correta, fase completa, progresso     |
| `--color-warning`  | `#E6A817` | Atenção, fase em progresso, dica               |
| `--color-error`    | `#D94452` | Resposta errada, streak quebrado, erro         |
| `--color-info`     | `#3A7BD5` | Dicas da IA, informações contextuais           |

### 1.5. Neutros

| Token                 | Hex       | Uso                                           |
|-----------------------|-----------|-----------------------------------------------|
| `--color-bg-primary`  | `#0F0F1A` | Fundo principal (dark mode)                    |
| `--color-bg-secondary`| `#1A1A2E` | Cards, painéis, sidebar                        |
| `--color-bg-elevated` | `#252540` | Elementos elevados, dropdowns, tooltips        |
| `--color-bg-surface`  | `#F5F0E8` | Fundo principal (light mode — tom de papel)    |
| `--color-text-primary`| `#EDEDED` | Texto principal (dark mode)                    |
| `--color-text-secondary`| `#A0A0B8` | Texto secundário, labels, placeholders       |
| `--color-text-dark`   | `#1A1A2E` | Texto principal (light mode)                   |
| `--color-border`      | `#2E2E48` | Bordas sutis, separadores                      |

### 1.6. Gradientes

```css
/* Gradiente principal — usado em CTAs e destaques */
--gradient-primary: linear-gradient(135deg, #D4940A 0%, #F2B830 100%);

/* Gradiente do Griô — identidade da marca */
--gradient-brand: linear-gradient(135deg, #2D1B69 0%, #D4940A 50%, #C45A3C 100%);

/* Gradiente de fundo — cards premium */
--gradient-surface: linear-gradient(180deg, #1A1A2E 0%, #0F0F1A 100%);

/* Gradiente de streak/conquista */
--gradient-streak: linear-gradient(135deg, #C45A3C 0%, #F2B830 100%);
```

---

## 2. Tipografia

### Fontes

| Uso         | Fonte                  | Fallback               | Motivo                                  |
|-------------|------------------------|-------------------------|-----------------------------------------|
| Títulos     | **Plus Jakarta Sans**  | `sans-serif`            | Geométrica, bold, moderna e amigável    |
| Corpo       | **Inter**              | `system-ui, sans-serif` | Máxima legibilidade em telas pequenas   |
| Código/Math | **JetBrains Mono**     | `monospace`             | Para fórmulas e código quando necessário |

### Escala Tipográfica

| Token          | Tamanho | Peso | Uso                          |
|----------------|---------|------|------------------------------|
| `--text-xs`    | 0.75rem | 400  | Captions, labels mínimos     |
| `--text-sm`    | 0.875rem| 400  | Texto auxiliar, metadata      |
| `--text-base`  | 1rem    | 400  | Corpo de texto padrão         |
| `--text-lg`    | 1.125rem| 500  | Subtítulos, destaques leves   |
| `--text-xl`    | 1.25rem | 600  | Títulos de cards              |
| `--text-2xl`   | 1.5rem  | 700  | Títulos de seção              |
| `--text-3xl`   | 1.875rem| 700  | Títulos de página             |
| `--text-4xl`   | 2.25rem | 800  | Hero/display                  |

---

## 3. Espaçamento

| Token          | Valor   | Uso                                  |
|----------------|---------|--------------------------------------|
| `--space-1`    | 0.25rem | Gaps mínimos, padding de ícones      |
| `--space-2`    | 0.5rem  | Padding interno de badges            |
| `--space-3`    | 0.75rem | Gap entre elementos inline           |
| `--space-4`    | 1rem    | Padding padrão de cards              |
| `--space-6`    | 1.5rem  | Gap entre cards, seções              |
| `--space-8`    | 2rem    | Margens de seção                     |
| `--space-12`   | 3rem    | Separação entre blocos grandes       |
| `--space-16`   | 4rem    | Padding de página                    |

---

## 4. Bordas e Sombras

```css
/* Bordas */
--radius-sm: 0.375rem;   /* Badges, tags */
--radius-md: 0.75rem;    /* Botões, inputs */
--radius-lg: 1rem;       /* Cards */
--radius-xl: 1.5rem;     /* Modais, painéis grandes */
--radius-full: 9999px;   /* Avatares, pills */

/* Sombras (dark mode) */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
--shadow-glow: 0 0 20px rgba(212, 148, 10, 0.3);  /* Glow dourado da marca */
```

---

## 5. Animações

```css
/* Transições padrão */
--transition-fast: 150ms ease;
--transition-base: 250ms ease;
--transition-slow: 400ms ease;
--transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);

/* Duração de micro-animações */
--duration-streak: 600ms;    /* Animação de streak */
--duration-level-up: 800ms;  /* Animação de level up */
--duration-confetti: 1500ms; /* Celebração de conquista */
```

---

## 6. Breakpoints (Mobile-First)

| Token          | Valor   | Dispositivo                |
|----------------|---------|----------------------------|
| `--bp-sm`      | 640px   | Celulares grandes           |
| `--bp-md`      | 768px   | Tablets                     |
| `--bp-lg`      | 1024px  | Laptops                     |
| `--bp-xl`      | 1280px  | Desktops                    |

**Regra:** Sempre desenvolver mobile-first. Media queries usam `min-width`.

---

## 7. Referências Culturais da Paleta

| Cor               | Referência Cultural                                                     |
|-------------------|-------------------------------------------------------------------------|
| Dourado âmbar     | Riqueza do conhecimento como herança coletiva. Ouro do saber, não do metal. |
| Índigo profundo   | O céu noturno sob o qual o Griô contava histórias. Profundidade e sabedoria. |
| Terracota         | A terra brasileira — raízes, origem, pertencimento.                      |
| Off-white quente  | O papel envelhecido da literatura de cordel, a tradição oral registrada.  |
