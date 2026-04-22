import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
from models.question import Question
from models.user import User
from core.neo4j import get_driver, close_driver

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_test_data(neo4j_driver):
    with neo4j_driver.session() as session:
        # Create concepts
        session.run("CREATE (:Concept {name: 'Test Concept 1'})")
        session.run("CREATE (:Concept {name: 'Test Concept 2'})")
    yield
    with neo4j_driver.session() as session:
        # Cleanup
        session.run("MATCH (c:Concept) DETACH DELETE c")

@pytest.fixture(scope="function")
def neo4j_driver():
    driver = get_driver()
    yield driver
    close_driver()
