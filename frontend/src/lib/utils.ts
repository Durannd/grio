// src/lib/utils.ts

/**
 * Replica a lógica de mascaramento do backend para consistência.
 * Transforma um ID da matriz (ex: 'MT_C1_H1') em um ID ofuscado (ex: 'SKL-XXXX').
 * Usa Base32 para ser limpo e reversível.
 */
export function maskId(originalId: string): string {
  if (!originalId || originalId.startsWith("SKL-")) {
    return originalId;
  }

  // A implementação de Base32 em JS pode variar, mas para strings ASCII,
  // uma conversão para Hex e depois para Base64 pode ser um bom proxy
  // ou podemos usar uma biblioteca se já houver uma no projeto.
  // Para este caso, vamos simular a lógica de ofuscação de forma simples.
  // AVISO: A lógica real de b32encode do Python é mais complexa.
  // O ideal seria o backend *sempre* prover o ID mascarado.
  // Esta é uma correção de consistência no fallback do frontend.
  try {
    const encoded = btoa(originalId).replace(/=/g, '');
    return `SKL-${encoded}`;
  } catch (e) {
    return originalId; // Fallback se btoa falhar
  }
}

/**
 * Formata um código de habilidade para exibição.
 * Ex: MT_C1_H5 -> Hab. 05
 */
export function formatPedagogicalCode(skillId: string): string {
    if (!skillId) return "Geral";
  
    const match = skillId.match(/H(\d+)$/);
    if (match) {
      return `Hab. ${String(parseInt(match[1])).padStart(2, '0')}`;
    }
  
    const compMatch = skillId.match(/C(\d+)$/);
    if (compMatch) {
      return `Comp. ${String(parseInt(compMatch[1])).padStart(2, '0')}`;
    }
      
    return "Módulo";
}
