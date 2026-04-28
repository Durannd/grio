"""
Global error handler: logs errors internally, hides details in production.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from core.logger import logger
import os


async def global_exception_handler(request: Request, exc: Exception):
    """Captura exceções não tratadas, loga e retorna resposta segura"""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)

    is_production = os.getenv("ENV", "development") == "production"
    detail = "Erro interno do servidor. Tente novamente." if is_production else str(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": detail}
    )
