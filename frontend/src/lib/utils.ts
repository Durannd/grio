export const areaMapping: Record<string, string> = {
  'LC': 'Linguagens',
  'MT': 'Matemática',
  'CH': 'Ciências Humanas',
  'CN': 'Ciências da Natureza'
};

/**
 * Formata um código pedagógico (ex: MT_C1_H1) para uma versão legível
 * (ex: Matemática: Competência 1 - Habilidade 1)
 */
export function formatPedagogicalCode(code: string): string {
  if (!code) return '';

  // Regex para capturar Área, Competência e Habilidade
  // Aceita formatos como MT_C1_H1 ou MT_C1 (apenas competência)
  const regex = /^([A-Z]{2})_C(\d+)(?:_H(\d+))?$/i;
  const match = code.match(regex);

  if (!match) return code;

  const [_, areaCode, competence, skill] = match;
  const areaName = areaMapping[areaCode] || areaCode;
  
  let formatted = `${areaName}: Competência ${competence}`;
  
  if (skill) {
    formatted += ` - Habilidade ${skill}`;
  }

  return formatted;
}
