const areaMapping = {
  'LC': 'Linguagens',
  'MT': 'Matemática',
  'CH': 'Ciências Humanas',
  'CN': 'Ciências da Natureza'
};

function formatPedagogicalCode(code) {
  if (!code) return '';
  const regex = /^([A-Z]{2})_C(\d+)(?:_H(\d+))?$/;
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

const tests = [
  'MT_C1_H1',
  'LC_C9_H30',
  'CH_C1_H5',
  'CN_C1_H1',
  'MT_C1',
  'INVALID_CODE'
];

tests.forEach(t => console.log(`${t} => ${formatPedagogicalCode(t)}`));
