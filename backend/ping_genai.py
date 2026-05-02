import sys
import os

# Adicionar o diretório atual ao sys.path para importar core.genai
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.genai import get_genai_client, generate_text
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

print("--- PING GENAI ---")
project = os.getenv("GOOGLE_CLOUD_PROJECT")
model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

print(f"Projeto: {project}")
print(f"Modelo: {model}")
print(f"Location: {os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')}")

print("\nEnviando requisição de teste...")

try:
    response = generate_text("Diga 'Pong' se você estiver funcionando corretamente.", model=model)
    print(f"\nResposta da IA: {response}")
    
    if "Pong" in response or "pong" in response.lower():
        print("\n✅ SUCESSO: A integração com o GenAI está funcionando!")
    else:
        print("\n⚠️ AVISO: A IA respondeu, mas não como esperado. Verifique o output acima.")

except Exception as e:
    print(f"\n❌ ERRO: Falha ao conectar com o GenAI.")
    print(f"Detalhes: {e}")
