import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
client = genai.Client()

class TestSchema(BaseModel):
    explanation: str = Field(description="Explicação")
    area: str = Field(description="Área")

try:
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents="Olá",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TestSchema,
        )
    )
    print("Success text:", response.text)
    if hasattr(response, 'parsed'):
        print("Success parsed:", response.parsed)
except Exception as e:
    print("Error:", e)
