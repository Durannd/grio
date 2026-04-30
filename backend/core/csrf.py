"""
CSRF Protection Module
Implementa geração e validação de tokens CSRF para proteger contra ataques cross-site request forgery
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Optional

CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_TTL = 3600  # 1 hora em segundos
CSRF_SECRET = os.getenv("CSRF_SECRET", "")

if not CSRF_SECRET:
    # Usar SECRET_KEY como fallback (menos ideal, mas funciona em dev)
    CSRF_SECRET = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


def generate_csrf_token() -> tuple[str, str]:
    """
    Gera um token CSRF com seu tempo de criação
    
    Retorna:
        (token_para_enviar, token_hash_para_servidor)
    """
    token = secrets.token_urlsafe(CSRF_TOKEN_LENGTH)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Hash do token para armazenar no servidor (mais seguro)
    token_hash = hashlib.sha256(
        f"{token}{CSRF_SECRET}".encode()
    ).hexdigest()
    
    return token, f"{token_hash}|{timestamp}"


def validate_csrf_token(token: str, stored_hash: str) -> bool:
    """
    Valida um token CSRF contra seu hash armazenado
    
    Args:
        token: Token enviado pelo cliente
        stored_hash: Hash + timestamp armazenado no servidor
    
    Retorna:
        True se o token é válido, False caso contrário
    """
    try:
        if "|" not in stored_hash:
            return False
        
        token_hash, timestamp_str = stored_hash.split("|", 1)
        
        # Verificar timestamp (não usar token expirado)
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now(timezone.utc)
        
        if (now - timestamp).total_seconds() > CSRF_TOKEN_TTL:
            return False
        
        # Verificar token hash
        computed_hash = hashlib.sha256(
            f"{token}{CSRF_SECRET}".encode()
        ).hexdigest()
        
        # Usar comparação segura contra timing attacks
        return hmac.compare_digest(computed_hash, token_hash)
    
    except (ValueError, AttributeError):
        return False


def get_csrf_token_expiry() -> str:
    """Retorna o timestamp de expiração do CSRF token"""
    expiry = datetime.now(timezone.utc) + timedelta(seconds=CSRF_TOKEN_TTL)
    return expiry.isoformat()


class CSRFValidator:
    """Validador CSRF para usar em middlewares ou dependências FastAPI"""
    
    def __init__(self):
        # Em produção, usar Redis com sets/lists expiráveis
        self.tokens: dict[str, list[str]] = {}
    
    def issue_token(self, session_id: str) -> str:
        """Emite um token CSRF para uma sessão e o adiciona à lista de tokens ativos (max 5)"""
        token, token_hash = generate_csrf_token()
        
        if session_id not in self.tokens:
            self.tokens[session_id] = []
            
        self.tokens[session_id].append(token_hash)
        
        # Evict old tokens (keep max 5 active tabs/requests per session to prevent memory leak)
        if len(self.tokens[session_id]) > 5:
            self.tokens[session_id].pop(0)
            
        return token
    
    def validate(self, session_id: str, token: str) -> bool:
        """Valida um token CSRF contra qualquer um dos tokens ativos da sessão"""
        if session_id not in self.tokens:
            return False
        
        # Check against all active tokens for this session
        for stored_hash in self.tokens[session_id]:
            if validate_csrf_token(token, stored_hash):
                return True
                
        return False
    
    def clear(self, session_id: str) -> None:
        """Remove todos os tokens CSRF de uma sessão"""
        self.tokens.pop(session_id, None)


# Instância global (em produção, seria melhor usar Redis)
csrf_validator = CSRFValidator()
