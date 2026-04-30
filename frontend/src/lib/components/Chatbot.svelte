<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { page } from '$app/stores';
  import { api } from '$lib/api';

  interface ChatMessage {
    role: 'user' | 'model';
    content: string;
  }

  // Ocultar automaticamente em rotas específicas para manter a sobriedade visual
  let isHiddenRoute = $derived(['/login', '/cadastro'].includes($page.url.pathname));

  let isOpen = $state(false);
  let message = $state("");
  let messages = $state([
    { text: "Olá! Sou o assistente do Griô. Como posso te ajudar? 📚", isBot: true }
  ]);
  let isLoading = $state(false);
  let chatHistory: ChatMessage[] = [];

  function toggleChat() {
    isOpen = !isOpen;
  }

  async function sendMessage() {
    if (!message.trim() || isLoading) return;

    const userMessage = message;
    messages = [...messages, { text: userMessage, isBot: false }];
    chatHistory = [...chatHistory, { role: 'user', content: userMessage }];
    message = "";
    isLoading = true;

    try {
      // Nota: O endpoint /mentor requer question_id. 
      // Esta é uma implementação genérica para assistência geral.
      // Em contexto de prova, pode ser extendido com question_id
      const response = await api.post('/chatbot/mentor', {
        question_id: 'general',
        selected_option_id: 0,
        chat_history: chatHistory,
        user_message: userMessage
      }) as { response: string };

      if (response && response.response) {
        const botMessage = response.response;
        messages = [...messages, { text: botMessage, isBot: true }];
        chatHistory = [...chatHistory, { role: 'model', content: botMessage }];
      } else {
        throw new Error('Resposta inválida do servidor');
      }
    } catch (error) {
      const errorMessage = "Desculpe, tive um problema ao processar sua mensagem. Tente novamente.";
      messages = [...messages, { text: errorMessage, isBot: true }];
      // Não adiciona erro ao histórico
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }
</script>

{#if !isHiddenRoute}
  <div class="chatbot-container" transition:fade>
    {#if isOpen}
    <div class="chat-window" in:fly={{ y: 20, duration: 300 }} out:fade>
      <div class="chat-header">
        <img src="/grio-logo.png" alt="Logo" class="header-logo" />
        <span>Assistente Griô</span>
        <button class="close-btn" onclick={toggleChat} aria-label="Fechar chat">&times;</button>
      </div>
      
      <div class="message-list">
        {#each messages as msg}
          <div class="message {msg.isBot ? 'bot' : 'user'}">
            <div class="bubble">{msg.text}</div>
          </div>
        {/each}
        {#if isLoading}
          <div class="message bot">
            <div class="bubble loading">...</div>
          </div>
        {/if}
      </div>

      <div class="chat-input">
        <input 
          type="text" 
          placeholder="Tire uma dúvida ou peça uma questão..." 
          bind:value={message}
          onkeydown={handleKeydown}
        />
        <button onclick={sendMessage} disabled={isLoading} aria-label="Enviar mensagem">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </div>
  {/if}

  <button class="float-btn" onclick={toggleChat} aria-label="Abrir Chatbot">
    <img src="/grio-logo.png" alt="Logo Griô" class="btn-logo" />
  </button>
</div>
{/if}

<style>
  .chatbot-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 1000;
  }

  .float-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--bg-base);
    border: 2px solid var(--primary);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    padding: 0;
    overflow: hidden;
  }

  .float-btn:hover {
    transform: scale(1.1);
  }

  .btn-logo {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .chat-window {
    position: absolute;
    bottom: 5rem;
    right: 0;
    width: 350px;
    height: 500px;
    background: var(--bg-base);
    border: var(--glass-border);
    border-radius: 1.5rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-header {
    background: var(--primary);
    color: white;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 600;
  }

  .header-logo {
    width: 24px;
    height: 24px;
    filter: brightness(0) invert(1);
  }

  .close-btn {
    margin-left: auto;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
  }

  .message-list {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: rgba(255,255,255,0.02);
  }

  .message {
    display: flex;
    flex-direction: column;
  }

  .message.user {
    align-items: flex-end;
  }

  .bubble {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .bot .bubble {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-bottom-left-radius: 0.2rem;
  }

  .user .bubble {
    background: var(--primary);
    color: white;
    border-bottom-right-radius: 0.2rem;
  }

  .chat-input {
    padding: 1rem;
    display: flex;
    gap: 0.5rem;
    background: var(--bg-base);
    border-top: var(--glass-border);
  }

  input {
    flex: 1;
    background: var(--bg-secondary);
    border: none;
    border-radius: 2rem;
    padding: 0.5rem 1rem;
    color: var(--text-primary);
    outline: none;
  }

  button:not(.float-btn):not(.close-btn) {
    background: none;
    border: none;
    color: var(--primary);
    cursor: pointer;
    display: flex;
    align-items: center;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading {
    letter-spacing: 0.2rem;
    font-weight: bold;
  }
</style>
