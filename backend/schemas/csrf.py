"""
Schemas para CSRF protection
"""

from pydantic import BaseModel, Field


class CSRFTokenResponse(BaseModel):
    """Resposta com token CSRF"""
    csrf_token: str = Field(..., description="Token CSRF para usar em requisições POST/PUT/DELETE")
    expires_at: str = Field(..., description="ISO 8601 timestamp de expiração")


class CSRFValidation(BaseModel):
    """Dados para validação CSRF em requisições"""
    csrf_token: str = Field(..., min_length=1, description="Token CSRF recebido do servidor")
