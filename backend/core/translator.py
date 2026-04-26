import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "skill_translations.json")

_translations = {}

def load_translations():
    global _translations
    if not _translations:
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                _translations = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar skill_translations.json: {e}")
            _translations = {}

def get_friendly_name(skill_id: str) -> str:
    """
    Retorna o nome amigável para uma sigla de habilidade.
    Exemplo: 'CN_C1_H1' -> 'Fenômenos Ondulatórios'
    """
    load_translations()
    return _translations.get(skill_id, f"Tópico {skill_id}")
