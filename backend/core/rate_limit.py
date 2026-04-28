"""
Rate Limiting para APIs de IA
Protege contra abuso e limita custos do Gemini
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException
import os

# Configurar limiter com Redis (se disponível) ou em-memory fallback
redis_url = os.getenv("REDIS_URL", None)

if redis_url:
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["200/minute"]  # Global fallback
    )
else:
    # Fallback para em-memory (não persistente entre restarts)
    from slowapi.util import get_remote_address
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200/minute"]
    )

# Rate limits específicos por endpoint
RATE_LIMITS = {
    # IA-heavy endpoints
    "mentor": "5/minute",           # Chat com IA (Gemini call)
    "analysis": "3/minute",         # Análise de assessment (Gemini call)
    "study_plan": "3/minute",       # Geração de plano (Gemini call)
    "microlesson": "5/minute",      # Micro-aulas (Gemini call)
    
    # Regular endpoints
    "assessment": "30/minute",      # Prova
    "learning_path": "20/minute",   # Buscar trilha
    "login": "10/minute",           # Proteção contra brute force
    "signup": "5/minute",           # Proteção contra spam
}

def get_rate_limit(endpoint_name: str) -> str:
    """Retorna o rate limit para um endpoint específico"""
    return RATE_LIMITS.get(endpoint_name, "100/minute")

async def rate_limit_error_handler(request, exc):
    """Handler customizado para erros de rate limit"""
    return HTTPException(
        status_code=429,
        detail="Muitas requisições. Tente novamente em alguns minutos."
    )
