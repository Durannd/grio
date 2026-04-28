from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/grio")
engine = create_engine(DATABASE_URL)

def sync_diagnostic_flags():
    with engine.connect() as conn:
        # Atualiza is_diagnostic_completed para todos os usuários que possuem pelo menos uma tentativa de diagnóstico
        print("Sincronizando flags de diagnóstico...")
        query = text("""
            UPDATE users 
            SET is_diagnostic_completed = TRUE 
            WHERE id IN (
                SELECT DISTINCT user_id 
                FROM assessment_attempts 
                WHERE type IN ('diagnostico', 'inicial')
            )
        """)
        result = conn.execute(query)
        conn.commit()
        print(f"Sincronização concluída. Linhas afetadas: {result.rowcount}")

if __name__ == "__main__":
    sync_diagnostic_flags()
