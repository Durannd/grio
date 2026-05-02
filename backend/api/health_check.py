from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
import redis
import logging

from database import get_db
from core.connections import get_neo4j_session, get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    postgres_status = "connected"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        postgres_status = "disconnected"

    neo4j_status = "connected"
    try:
        neo4j_session.run("RETURN 1")
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        neo4j_status = "disconnected"

    redis_status = "connected"
    try:
        redis_client.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "disconnected"

    status = "ok" if all(s == "connected" for s in [postgres_status, neo4j_status, redis_status]) else "degraded"

    return {
        "status": status,
        "postgresql": postgres_status,
        "neo4j": neo4j_status,
        "redis": redis_status
    }
