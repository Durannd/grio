from fastapi.testclient import TestClient
from backend.main import app
from backend.core.neo4j import get_driver
import pytest

client = TestClient(app)

def test_submit_assessment(client, neo4j_driver):
    # Create test concepts
    with neo4j_driver.session() as session:
        session.run("CREATE (:Concept {name: 'Test Concept 1'})")
        session.run("CREATE (:Concept {name: 'Test Concept 2'})")
    # Create a test user
    user_response = client.post("/api/v1/users/", json={"name": "Test User", "email": "test-assessment@example.com", "password": "test"})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Get assessment questions
    assessment_response = client.get("/api/v1/assessment")
    questions = assessment_response.json()["questions"]

    # Select the correct answer for the first question
    first_question = questions[0]
    correct_option_id = first_question["correct_option_id"]

    # Submit the assessment
    submission_data = {
        "user_id": user_id,
        "answers": [{"question_id": first_question["id"], "selected_option_id": correct_option_id}]
    }
    response = client.post("/api/v1/assessment/submit", json=submission_data)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200

    # Verify proficiency in Neo4j
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(c:Concept) RETURN r.score as score",
            user_id=user_id
        )
        record = result.single()
        assert record is not None
        assert record["score"] == 1.0

    # Cleanup
    with neo4j_driver.session() as session:
        session.run("MATCH (u:User {id: $user_id}) DETACH DELETE u", user_id=user_id)
