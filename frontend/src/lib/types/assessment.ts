export interface Question {
  id: number;
  text: string;
  difficulty: 'facil' | 'media' | 'dificil';
  concept_name: string;
}
