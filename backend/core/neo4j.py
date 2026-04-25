from neo4j import GraphDatabase
import neo4j
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = None

def get_driver():
    global driver
    if driver is None:
        # Para ignorar erro de SSL em Aura, mudamos o protocolo para +ssc (Self-Signed Certificate)
        uri = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
        driver = GraphDatabase.driver(
            uri, 
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    return driver

def close_driver():
    global driver
    if driver is not None:
        driver.close()
        driver = None

def get_session():
    with get_driver().session() as session:
        yield session
