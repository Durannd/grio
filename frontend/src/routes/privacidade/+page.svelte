<script lang="ts">
  // Política de Privacidade Estática (LGPD)
</script>

<svelte:head>
  <title>Política de Privacidade - Griô</title>
</svelte:head>

<div class="legal-container container animate-slide-up">
  <div class="glass-panel content-box">
    <h1>Política de Privacidade (LGPD)</h1>
    <p class="last-updated">Última atualização: {new Date().toLocaleDateString('pt-BR')}</p>

    <div class="prose">
      <h2>1. Nosso Compromisso com a sua Privacidade</h2>
      <p>O Griô leva a sua privacidade a sério. Esta política descreve, em conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018 - LGPD), como coletamos, usamos, armazenamos e protegemos seus dados.</p>

      <h2>2. Dados Coletados</h2>
      <p>Coletamos dois tipos principais de dados:</p>
      <ul>
        <li><strong>Dados Cadastrais:</strong> Nome completo, endereço de e-mail e senha (armazenada de forma criptografada irreversível utilizando <em>bcrypt</em>).</li>
        <li><strong>Dados Comportamentais e Pedagógicos:</strong> Seu histórico de respostas, opções selecionadas, tempo gasto em cada questão e sua interação com o Mentor Socrático (Chatbot).</li>
      </ul>

      <h2>3. Finalidade do Tratamento (Por que coletamos?)</h2>
      <p>Os dados comportamentais são essenciais para o funcionamento central do Griô. Eles alimentam nosso <em>Knowledge Graph</em> (Grafo de Conhecimento) para:</p>
      <ul>
        <li>Mapear sua proficiência acadêmica com precisão matemática.</li>
        <li>Identificar lacunas de conhecimento (erros).</li>
        <li>Personalizar a geração de Planos de Estudo e Micro-aulas através de Inteligência Artificial.</li>
        <li>Auditar respostas para detectar comportamentos anômalos (chutes) e garantir a qualidade do seu diagnóstico.</li>
      </ul>

      <h2>4. Compartilhamento de Dados com Terceiros</h2>
      <p>O Griô opera utilizando a infraestrutura da <strong>API do Google Gemini</strong> para processamento de linguagem natural e Inteligência Artificial. Reconhecemos e informamos que:</p>
      <ul>
        <li>O conteúdo das interações no Chatbot (Mentor Socrático) e os dados agregados das suas métricas de proficiência são enviados de forma anônima e contextual à API do Google.</li>
        <li><strong>Não enviamos seus dados pessoais de identificação (PII)</strong>, como nome completo ou e-mail, para a API do Gemini. As requisições são compostas estritamente pelo contexto educacional.</li>
      </ul>

      <h2>5. Segurança da Informação</h2>
      <p>Empregamos tecnologias de segurança avançadas, como proteção contra ataques CSRF (via <em>tokens</em> dinâmicos), proteção contra ataques de força bruta, mascaramento de IDs internos e uso exclusivo de cookies <em>HttpOnly</em> (que não podem ser acessados por scripts maliciosos no seu navegador) para proteger sua sessão e seus dados.</p>

      <h2>6. Seus Direitos (Art. 18 da LGPD)</h2>
      <p>Você tem o direito de:</p>
      <ul>
        <li>Confirmar a existência de tratamento de dados.</li>
        <li>Acessar seus dados através do Painel da sua conta.</li>
        <li>Corrigir dados incompletos ou desatualizados.</li>
        <li>Solicitar a exclusão total da sua conta e de todo o seu rastro de dados pedagógicos (salvo os dados necessários para cumprimento de obrigação legal).</li>
      </ul>

      <h2>7. Contato do Encarregado de Dados (DPO)</h2>
      <p>Para exercer seus direitos ou tirar dúvidas sobre o tratamento dos seus dados, entre em contato através do e-mail da plataforma disponibilizado nos canais oficiais de suporte.</p>
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

  .prose strong, .prose em {
    color: var(--primary-light);
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