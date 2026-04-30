<script lang="ts">
  // Termos de Uso Estático
</script>

<svelte:head>
  <title>Termos de Uso - Griô</title>
</svelte:head>

<div class="legal-container container animate-slide-up">
  <div class="glass-panel content-box">
    <h1>Termos de Uso</h1>
    <p class="last-updated">Última atualização: {new Date().toLocaleDateString('pt-BR')}</p>

    <div class="prose">
      <h2>1. Aceitação dos Termos</h2>
      <p>Ao criar uma conta e utilizar a plataforma Griô, você concorda com estes Termos de Uso. Caso não concorde, não deverá utilizar nossos serviços.</p>

      <h2>2. Natureza do Serviço</h2>
      <p>O Griô é uma ferramenta educacional baseada em Inteligência Artificial e Grafos de Conhecimento, destinada a auxiliar estudantes em sua preparação acadêmica (ex: ENEM). <strong>O Griô não substitui o ensino formal, professores capacitados ou materiais didáticos oficiais.</strong></p>

      <h2>3. Uso de Inteligência Artificial</h2>
      <p>Você reconhece e concorda que:</p>
      <ul>
        <li>O conteúdo de diagnóstico, planos de estudo, micro-aulas e mentorias são gerados com o auxílio de IA Generativa.</li>
        <li>Embora utilizemos técnicas de RAG (Retrieval-Augmented Generation) para garantir a mais alta precisão técnica baseada em questões reais, <strong>a Inteligência Artificial é suscetível a alucinações e erros pontuais.</strong></li>
        <li>O usuário deve utilizar as informações fornecidas pelo Griô com pensamento crítico.</li>
      </ul>

      <h2>4. Propriedade Intelectual</h2>
      <p>A estrutura de grafos, matrizes de referência ofuscadas, a marca Griô e os algoritmos de auditoria e propagação de proficiência são propriedade intelectual exclusiva da plataforma. Você não pode descompilar, aplicar engenharia reversa ou tentar extrair nossa malha de dados pedagógicos (Knowledge Graph).</p>

      <h2>5. Conta do Usuário e Segurança</h2>
      <p>Você é responsável por manter a confidencialidade de suas credenciais de acesso. O Griô reserva-se o direito de suspender contas que apresentem comportamento automatizado (uso de bots) para responder questões, visando proteger a integridade de nossa amostragem de dados e custos de infraestrutura.</p>

      <h2>6. Limitação de Responsabilidade</h2>
      <p>O Griô não garante aprovação em exames oficiais (como o ENEM). O sucesso do usuário depende exclusivamente de seu próprio esforço e dedicação.</p>

      <h2>7. Modificações dos Termos</h2>
      <p>O Griô pode atualizar estes termos a qualquer momento. Notificaremos os usuários sobre mudanças significativas através da plataforma.</p>
    </div>
  </div>
</div>

<style>
  .legal-container {
    padding-top: 3rem;
    padding-bottom: 6rem;
    max-width: 800px;
  }

  .content-box {
    padding: 3rem;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    color: var(--primary-light);
  }

  .last-updated {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 3rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 1rem;
  }

  .prose h2 {
    font-size: 1.5rem;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
  }

  .prose p {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  .prose ul {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
  }

  .prose li {
    margin-bottom: 0.5rem;
  }

  .prose strong {
    color: var(--primary-light);
    font-weight: 600;
  }

  @media (max-width: 768px) {
    .content-box {
      padding: 2rem 1.5rem;
    }
    
    h1 {
      font-size: 2rem;
    }
  }
</style>