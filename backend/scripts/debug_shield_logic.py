import sys
import os
from dotenv import load_dotenv

# Adiciona o diretório backend ao path para poder importar core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.translator import mask_id, unmask_id, get_friendly_name, get_friendly_code

def test_translator():
    print("=== DEBUG: TRANSLATOR LOGIC ===")
    
    # 1. Teste de Máscara
    original = "MT_C1_H1"
    masked = mask_id(original)
    print(f"Original: {original} -> Masked: {masked}")
    assert masked.startswith("SKL-")
    
    # 2. Teste de Desmascaramento
    unmasked = unmask_id(masked)
    print(f"Masked: {masked} -> Unmasked: {unmasked}")
    assert unmasked == original
    
    # 3. Teste de Nome Amigável (Prioridades)
    # Caso A: Existe no banco (simulado)
    name_db = get_friendly_name(original, db_friendly_name="Geometria")
    print(f"Prioridade Banco: {name_db}")
    assert name_db == "Geometria"
    
    # Caso B: Existe no JSON (MT_C1_H1 está no JSON)
    name_json = get_friendly_name(original)
    print(f"Prioridade JSON: {name_json}")
    assert name_json == "Geometria Plana"
    
    # Caso C: Não existe em nenhum lugar (Usa Friendly Code)
    unknown_id = "XX_C9_H99"
    name_fallback = get_friendly_name(unknown_id)
    print(f"Prioridade Fallback: {name_fallback}")
    assert name_fallback == "Hab. 99"

    # 4. Teste de Friendly Code
    print(f"Friendly Code (Habilidade): {get_friendly_code('MT_C1_H05')}")
    print(f"Friendly Code (Competência): {get_friendly_code('MT_C3')}")
    print(f"Friendly Code (Inválido): {get_friendly_code('ALGO_ESTRANHO')}")

    print("\n✅ TRANSLATOR: TUDO OK")

if __name__ == "__main__":
    try:
        test_translator()
    except Exception as e:
        print(f"\n❌ ERRO ENCONTRADO: {e}")
        sys.exit(1)
