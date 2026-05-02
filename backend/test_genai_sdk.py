import os
from dotenv import load_dotenv
from core.genai import get_genai_client
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
client = get_genai_client()

class TestSchema(BaseModel):
    explanation: str = Field(description="Explicação")
    area: str = Field(description="Área")

try:
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    print(f"Testando com o modelo: {model_name}")
    response = client.models.generate_content(
        model=model_name,
        contents="Olá, responda no formato JSON de teste.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TestSchema,
        )
    )
    print("Success text:", response.text)
except Exception as e:
    print("Error:", e)
