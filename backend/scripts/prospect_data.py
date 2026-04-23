import httpx
import json
import os
import time

# Configurações
BASE_URL = "https://datasets-server.huggingface.co/rows?dataset=eduagarcia/enem_challenge&config=default&split=train"
OUTPUT_FILE = "scripts/enem_sample.json"

def fetch_data():
    all_questions = []
    offset = 0
    length = 100
    max_questions = 1000 # Vamos pegar 1000 para começar

    print(f"Iniciando busca de {max_questions} questões...")
    
    try:
        with httpx.Client() as client:
            while offset < max_questions:
                url = f"{BASE_URL}&offset={offset}&length={length}"
                print(f"Buscando offset {offset}...")
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                questions = [row["row"] for row in data["rows"]]
                all_questions.extend(questions)
                
                if len(questions) < length:
                    break # Fim dos dados
                    
                offset += length
                time.sleep(1) # Evitar rate limit
            
            # Salvar no arquivo
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_questions, f, indent=2, ensure_ascii=False)
            
            print(f"Sucesso! {len(all_questions)} questões salvas em {OUTPUT_FILE}")
            
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")

if __name__ == "__main__":
    fetch_data()
