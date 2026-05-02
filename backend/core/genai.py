from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from core.logger import logger

load_dotenv()

def get_genai_client():
    """
    Retorna um cliente configurado para o Google GenAI.
    Se GOOGLE_CLOUD_PROJECT estiver definido, utiliza Vertex AI (para usar os créditos de $1000).
    Caso contrário, utiliza a GEMINI_API_KEY do AI Studio.
    """
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    api_key = os.getenv("GEMINI_API_KEY")
    
    try:
        if project:
            # Em ambientes Docker/Local autenticados via gcloud, o SDK busca ADC.
            # Se GOOGLE_APPLICATION_CREDENTIALS não existir, ele tentará os caminhos padrão do sistema.
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if creds_path:
                logger.info(f"Vertex AI: Usando Service Account via {creds_path}")
            else:
                logger.info(f"Vertex AI: Iniciando via ADC (Application Default Credentials) no Projeto {project}")
            
            return genai.Client(
                vertexai=True,
                project=project,
                location=location
            )
        elif api_key:
            logger.info("Iniciando cliente Gemini via AI Studio (API Key)")
            return genai.Client(api_key=api_key)
        else:
            logger.error("Nenhuma credencial de GenAI encontrada (.env sem GEMINI_API_KEY ou GOOGLE_CLOUD_PROJECT)")
            return None
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente GenAI: {e}")
        return None

def generate_text(prompt: str, system_instruction: str = None, model: str = None):
    """
    Função utilitária para geração simples de texto.
    """
    client = get_genai_client()
    if not client:
        return "Erro: IA não configurada."
    
    model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Erro na geração de conteúdo: {e}")
        return f"Erro na IA: {str(e)}"
