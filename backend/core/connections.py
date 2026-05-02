import os
from neo4j import GraphDatabase
import redis
from dotenv import load_dotenv

load_dotenv()

# Neo4j Driver
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_neo4j_session():
    """
    Dependency to get a Neo4j session.
    """
    session = neo4j_driver.session()
    try:
        yield session
    finally:
        session.close()

# Redis Client
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

def get_redis_client():
    """
    Dependency to get a Redis client.
    """
    return redis_client
