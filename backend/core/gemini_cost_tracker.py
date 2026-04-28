"""
Gemini API Cost Tracker
Monitora e registra uso de API Gemini para controle de custos
"""

import time
from datetime import datetime, timezone
from typing import Optional
from core.logger import logger
import json

# Custo aproximado por token (baseado em documentação Google)
# https://ai.google.dev/pricing
GEMINI_COST_PER_1K_INPUT = 0.00075  # $0.00075 per 1K input tokens
GEMINI_COST_PER_1K_OUTPUT = 0.003   # $0.003 per 1K output tokens


class GeminiCostTracker:
    """Rastreia custos de uso do Gemini API"""
    
    def __init__(self):
        self.requests = []
        self.total_cost = 0.0
    
    def estimate_tokens(self, text: str) -> int:
        """Estimativa simples de tokens (aprox. 1 token por 4 caracteres)"""
        return max(1, len(text) // 4)
    
    def log_request(
        self,
        user_id: str,
        endpoint: str,
        prompt_text: str,
        response_text: Optional[str] = None,
        duration_ms: float = 0,
        status: str = "success",
        error: Optional[str] = None
    ) -> dict:
        """
        Registra uma requisição ao Gemini
        
        Retorna dict com detalhes do custo
        """
        input_tokens = self.estimate_tokens(prompt_text)
        output_tokens = self.estimate_tokens(response_text) if response_text else 0
        
        input_cost = (input_tokens / 1000) * GEMINI_COST_PER_1K_INPUT
        output_cost = (output_tokens / 1000) * GEMINI_COST_PER_1K_OUTPUT
        total_cost = input_cost + output_cost
        
        self.total_cost += total_cost
        
        request_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "endpoint": endpoint,
            "status": status,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "duration_ms": round(duration_ms, 2),
            "error": error,
        }
        
        self.requests.append(request_record)
        
        # Log estruturado
        logger.info(
            f"Gemini API call: {endpoint} | Tokens: {input_tokens}+{output_tokens} | "
            f"Cost: ${total_cost:.6f} | Duration: {duration_ms:.0f}ms | Status: {status}"
        )
        
        return request_record
    
    def get_session_summary(self) -> dict:
        """Retorna resumo de custos da sessão"""
        return {
            "total_requests": len(self.requests),
            "total_tokens": sum(r["total_tokens"] for r in self.requests),
            "total_cost_usd": round(self.total_cost, 6),
            "average_cost_per_request": round(
                self.total_cost / len(self.requests) if self.requests else 0,
                6
            ),
            "average_duration_ms": round(
                sum(r["duration_ms"] for r in self.requests) / len(self.requests)
                if self.requests else 0,
                2
            ),
        }
    
    def get_user_summary(self, user_id: str) -> dict:
        """Retorna resumo de custos por usuário"""
        user_requests = [r for r in self.requests if r["user_id"] == user_id]
        total_cost = sum(r["estimated_cost_usd"] for r in user_requests)
        
        return {
            "user_id": user_id,
            "request_count": len(user_requests),
            "total_tokens": sum(r["total_tokens"] for r in user_requests),
            "total_cost_usd": round(total_cost, 6),
            "requests": user_requests,
        }
    
    def export_logs(self, filepath: str):
        """Exporta logs para arquivo JSON para análise"""
        with open(filepath, "w") as f:
            json.dump({
                "summary": self.get_session_summary(),
                "requests": self.requests,
            }, f, indent=2)
        logger.info(f"Exported Gemini cost logs to {filepath}")


# Instância global
gemini_tracker = GeminiCostTracker()


def track_gemini_call(user_id: str, endpoint: str):
    """Decorator para rastrear chamadas Gemini"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            prompt = args[0] if args else ""
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                response_text = str(result) if result else ""
                gemini_tracker.log_request(
                    user_id=user_id,
                    endpoint=endpoint,
                    prompt_text=str(prompt),
                    response_text=response_text,
                    duration_ms=duration_ms,
                    status="success"
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                gemini_tracker.log_request(
                    user_id=user_id,
                    endpoint=endpoint,
                    prompt_text=str(prompt),
                    duration_ms=duration_ms,
                    status="error",
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator
