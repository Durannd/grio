import httpx
import json
import os

# Configurações
DATASET_URL = "https://datasets-server.huggingface.co/rows?dataset=eduagarcia/enem_challenge&config=default&split=train&offset=0&length=100"
OUTPUT_FILE = "backend/scripts/enem_sample.json"

def fetch_data():
    print(f"Buscando dados de: {DATASET_URL}")
    try:
        with httpx.Client() as client:
            response = client.get(DATASET_URL)
            response.raise_for_status()
            data = response.json()
            
            # Extrair apenas a linha (row) de cada item
            questions = [row["row"] for row in data["rows"]]
            
            # Salvar no arquivo
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            print(f"Sucesso! {len(questions)} questões salvas em {OUTPUT_FILE}")
            
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")

if __name__ == "__main__":
    fetch_data()
