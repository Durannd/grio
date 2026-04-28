import json
import os
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "skill_translations.json")

_translations = {}
_mask_cache = {}
_unmask_cache = {}

def load_translations():
    global _translations
    if not _translations:
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                _translations = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar skill_translations.json: {e}")
            _translations = {}

def get_friendly_name(skill_id: str, db_friendly_name: str = None) -> str:
    """
    Retorna o nome amigável para uma sigla de habilidade.
    Prioridade:
    1. Nome vindo do Banco de Dados (Neo4j)
    2. Tradução manual no JSON
    3. Código formatado (ex: Hab. 01)
    """
    if db_friendly_name and not db_friendly_name.startswith("Hab. "):
         return db_friendly_name

    actual_id = unmask_id(skill_id)
    load_translations()
    
    if actual_id in _translations:
        return _translations[actual_id]
        
    # Se o banco mandou um "Hab. XX" ou nada, tenta gerar o código bonito
    return get_friendly_code(skill_id)

def get_friendly_code(skill_id: str) -> str:
    """
    Gera um código visualmente limpo para o usuário.
    Exemplo: 'MT_C1_H01' -> 'Hab. 01'
    """
    actual_id = unmask_id(skill_id)
    if not actual_id:
        return "Geral"
    
    # Extrai o número da habilidade (final da string)
    import re
    match = re.search(r'H(\d+)$', actual_id)
    if match:
        return f"Hab. {int(match.group(1)):02d}"
    
    # Fallback para competência se não houver habilidade
    match_comp = re.search(r'C(\d+)$', actual_id)
    if match_comp:
        return f"Comp. {int(match_comp.group(1)):02d}"
        
    return "Módulo"

def mask_id(original_id: str) -> str:
    """
    Masca um ID da matriz ENEM em um código ofuscado.
    Exemplo: 'MT_C1_H1' -> 'SKL-A71B' (Exemplo)
    Utiliza Base32 para um visual limpo e reversível.
    """
    if not original_id or original_id.startswith("SKL-"):
        return original_id
    
    if original_id in _mask_cache:
        return _mask_cache[original_id]
        
    # Reversível via Base32 (remove preenchimento)
    encoded = base64.b32encode(original_id.encode()).decode().strip("=")
    masked = f"SKL-{encoded}"
    
    _mask_cache[original_id] = masked
    _unmask_cache[masked] = original_id
    
    return masked

def unmask_id(masked_id: str) -> str:
    """
    Converte um código ofuscado de volta para o ID original.
    """
    if not masked_id or not str(masked_id).startswith("SKL-"):
        return masked_id
        
    if masked_id in _unmask_cache:
        return _unmask_cache[masked_id]
        
    try:
        pure_base32 = masked_id[4:]
        # Adiciona preenchimento se necessário
        padding = len(pure_base32) % 8
        if padding:
            pure_base32 += "=" * (8 - padding)
            
        original_id = base64.b32decode(pure_base32.encode()).decode()
        
        _unmask_cache[masked_id] = original_id
        _mask_cache[original_id] = masked_id
        
        return original_id
    except Exception:
        return masked_id
