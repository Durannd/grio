# Griô — Design Tokens & Guia Visual

> **Este arquivo é a fonte de verdade para cores, tipografia e espaçamento do projeto Griô.**
> Toda decisão de frontend deve seguir estes tokens.

---

## 1. Paleta de Cores

### 1.1. Cores Principais

| Token                | Hex       | HSL                  | Uso                                              |
|----------------------|-----------|----------------------|--------------------------------------------------|
| `--color-primary`    | `#C9A05E` | `hsl(42, 51%, 58%)`  | Dourado Logo: Ações principais, ícones de marca  |
| `--color-primary-light` | `#DFB97B` | `hsl(42, 60%, 68%)` | Hover de botões dourados, reflexos, glows        |
| `--color-primary-dark`  | `#9A753B` | `hsl(42, 45%, 42%)` | Bordas e estados pressed                         |

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
| `--color-bg-primary`  | `#0A0A0A` | Fundo principal (Absolute Dark)                |
| `--color-bg-secondary`| `#141414` | Cards, painéis de conteúdo                     |
| `--color-bg-elevated` | `#1A1A1A` | Dropdowns, tooltips, modais                   |
| `--color-bg-surface`  | `#FFFFFF` | Reservado para uso invertido (light mode)      |
| `--color-text-primary`| `#FAFAFA` | Texto principal                               |
| `--color-text-secondary`| `#A3A3A3`| Texto de suporte, descrições secundárias      |
| `--color-text-dark`   | `#0A0A0A` | Texto escuro sobre fundos dourados            |
| `--color-border`      | `#262626` | Separadores subtis em vidro                   |

### 1.6. Gradientes

```css
/* Gradiente Dourado (Storytelling Accent) */
--gradient-primary: linear-gradient(135deg, #DFB97B 0%, #C9A05E 50%, #9A753B 100%);

/* Fundo Principal Translúcido (Liquid Glass) */
--glass-bg: rgba(20, 20, 20, 0.4);
--glass-border: 1px solid rgba(250, 250, 250, 0.05);
--glass-blur: blur(12px);

/* Gradiente de fundo */
--gradient-surface: radial-gradient(circle at 50% 0%, #1A1A1A 0%, #0A0A0A 100%);
```

---

## 2. Tipografia

### Fontes

| Uso         | Fonte                  | Fallback               | Motivo                                  |
|-------------|------------------------|-------------------------|-----------------------------------------|
| Títulos     | **Playfair Display**   | `serif`                 | Elegância, storytelling, luxo, sabedoria |
| Corpo       | **Inter**              | `system-ui, sans-serif` | Máxima legibilidade em interfaces       |
| Código/Math | **JetBrains Mono**     | `monospace`             | Para fórmulas matemáticas e código      |

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
/* Bordas (Liquid Glass usa bordas ligeiramente mais suaves) */
--radius-sm: 0.25rem;    /* Badges */
--radius-md: 0.5rem;     /* Inputs, Botões */
--radius-lg: 1rem;       /* Cards */
--radius-xl: 1.5rem;     /* Modais grandes */
--radius-full: 9999px;   /* Pills, avatares */

/* Sombras Premium / Glows Dourados */
--shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
--shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.6);
--shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.8);
--shadow-glow: 0 0 24px rgba(201, 160, 94, 0.25); /* Glow elegante com a cor do logotipo */
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
| Ouro Griô         | Representa a herança inestimável do conhecimento e a elegância atemporal.|
| Absolute Dark     | O vazio inicial e o céu profundo onde o conhecimento brilha.             |
| Glassmorphism     | A fluidez das ideias e a transparência da sabedoria.                     |
