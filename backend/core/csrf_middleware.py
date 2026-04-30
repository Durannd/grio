"""
CSRF Middleware para FastAPI
Valida tokens CSRF em requisições POST/PUT/DELETE
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import json
from core.csrf import csrf_validator
from core.logger import logger


class CSRFMiddleware:
    """Middleware para validação de CSRF tokens"""
    
    # Endpoints que não precisam de CSRF (GET apenas, login, signup, etc)
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/signup",
        "/api/v1/auth/logout",
        "/api/v1/auth/csrf-token",
        "/api/v1/auth/me",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    # Métodos HTTP que não precisam de CSRF
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    
    def __init__(self, app):
        """Inicializar middleware com a aplicação"""
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Processa a requisição e valida CSRF se necessário"""
        
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Pular validação para requisições seguras (GET, HEAD, OPTIONS)
        if request.method in self.SAFE_METHODS:
            await self.app(scope, receive, send)
            return
        
        # Pular validação para endpoints isentos
        if request.url.path in self.EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return
        
        # Validar CSRF para requisições não-seguras (POST, PUT, DELETE, PATCH)
        try:
            csrf_token = await self._extract_csrf_token(request)
            
            if not csrf_token:
                logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
                response = JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Token CSRF ausente ou inválido"}
                )
                await response(scope, receive, send)
                return
            
            # Obter token armazenado da sessão
            session_id = self._get_session_id(request)
            
            if not csrf_validator.validate(session_id, csrf_token):
                logger.warning(f"CSRF validation failed for {request.method} {request.url.path} from {request.client.host}")
                response = JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Token CSRF inválido ou expirado"}
                )
                await response(scope, receive, send)
                return
            
            # Nota: Não consumimos o token imediatamente para permitir requisições paralelas do frontend.
            # O frontend deve atualizar o token via header da resposta se necessário.
            new_token = csrf_validator.issue_token(session_id)
            
        except Exception as e:
            logger.error(f"CSRF middleware error: {str(e)}")
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Erro ao processar token de segurança"}
            )
            await response(scope, receive, send)
            return
        
        # Wrapper para adicionar header na resposta
        async def send_with_csrf_header(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-csrf-token", new_token.encode()))
                message["headers"] = headers
            await send(message)
        
        # Processar a requisição
        await self.app(scope, receive, send_with_csrf_header)
    
    async def _extract_csrf_token(self, request: Request) -> str | None:
        """Extrai token CSRF do header ou corpo da requisição"""
        
        # Verificar header primeiro (recomendado)
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # Fallback para body (JSON)
        try:
            if request.method in {"POST", "PUT", "PATCH"}:
                body = await request.body()
                if body:
                    data = json.loads(body)
                    token = data.get("csrf_token")
                    if token:
                        return token
        except Exception:
            pass
        
        return None
    
    def _get_session_id(self, request: Request) -> str:
        """Obtém ID da sessão do usuário (usa IP + User-Agent como fallback)"""
        # Prioriza X-Forwarded-For se estiver atrás de um proxy (ex: Docker)
        client_ip = request.headers.get("x-forwarded-for")
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
            
        user_agent = request.headers.get("user-agent", "")
        
        return f"{client_ip}:{user_agent}"


def setup_csrf_middleware(app):
    """Adiciona CSRF middleware à aplicação"""
    # Check if CSRF is enabled (default: disabled for testing, enable in production)
    import os
    if os.getenv("ENABLE_CSRF", "false").lower() == "true":
        app.add_middleware(CSRFMiddleware)
