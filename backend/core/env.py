import os
import sys

def validate_environment():
    """Valida variáveis de ambiente críticas na startup"""
    
    required_vars = {
        "GEMINI_API_KEY": "Google Gemini API key for AI features",
        "SECRET_KEY": "Secret key for JWT token signing (min 32 chars)",
        "NEO4J_URI": "Neo4j database connection URI",
        "NEO4J_USER": "Neo4j username",
        "NEO4J_PASSWORD": "Neo4j password",
        "DATABASE_URL": "PostgreSQL connection string",
    }
    
    missing_vars = []
    invalid_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        
        if not value:
            missing_vars.append(f"  - {var}: {description}")
        else:
            # Validações específicas
            if var == "SECRET_KEY" and len(value) < 32:
                invalid_vars.append(f"  - {var}: Must be at least 32 characters (currently {len(value)})")
            elif var == "GEMINI_API_KEY" and len(value) < 20:
                invalid_vars.append(f"  - {var}: Looks too short for a valid API key")
    
    if missing_vars:
        print("❌ MISSING ENVIRONMENT VARIABLES:", file=sys.stderr)
        for var in missing_vars:
            print(var, file=sys.stderr)
        raise RuntimeError("Missing critical environment variables")
    
    if invalid_vars:
        print("⚠️  INVALID ENVIRONMENT VARIABLES:", file=sys.stderr)
        for var in invalid_vars:
            print(var, file=sys.stderr)
        raise RuntimeError("Invalid environment variable values")
    
    print("✅ Environment validation passed")
